module_name = 'RemoteControl_v25.py'

import GPIOPico_v28 as GPIO
ColObjects = GPIO.ColObjects
import utime
import rp2

@rp2.asm_pio()
def measure():
    wrap_target()
    wait(0,pin,0)  #  don't start in the middle of a pulse
    wait(1,pin,0)
    mov(x,invert(null))
    label('loop')
    jmp(x_dec,'pin_on') #  Note: x will never be zero. We just want the decrement
    nop()
    label('pin_on')
    jmp(pin, 'loop')
    mov(isr,invert(x))
    push(noblock)
    wrap()

class StateMachine(ColObjects.PIO):
    
    valid_codes = ['MEASURE']

    def __init__(self, name, code, pin_no, hertz=100000):
        if code not in StateMachine.valid_codes:
            raise ColObjects.ColError ('**' + name + '**' + code + 'not in' + StateMachine.valid_codes)
        pio_block = 0  #  convention is block 0 for remote control, block 1 for NeoPixel
        super().__init__(name, pio_block)
        self.code = code
        self.gpio = GPIO.ControlPin(self.name + '_control', pin_no)
        self.pin_no = pin_no
        self.pin = self.gpio.pin
        self.instance = rp2.StateMachine(self.pio_no, measure, freq=hertz, in_base=self.pin, jmp_pin=self.pin)
        self.instance.active(1)
        self.valid = True
    def get_next_blocking(self):
        self.value =  self.instance.get()
        return self.value
    def get_latest(self):
        self.value = None
        while self.instance.rx_fifo():
            self.value = self.instance.get()
        return self.value
    def close(self):
        self.instance.active(0)
        self.gpio.close()
        super().close()

class RCSwitch(ColObjects.ColObj):
    def __init__(self, name, state_machine, intervals, values):  #  sequence of positions
        response = super().__init__(name)
        self.intervals = intervals
        self.values = values
        self.state_machine = state_machine
        if not self.state_machine.valid:
            raise ColObjects.ColError ('**** bad sm ' + self.state_machine.name)
        self.previous = 'OFF'
    def __str__(self):
        return self.name + '_' + self.state_machine.name
    def close(self):
        self.state_machine.close()
    def get(self):
        self.value = self.state_machine.get_latest()
        if self.value is not None:
            for i in range(len(self.intervals)):
                if self.value < self.intervals[i]:
                    self.previous = self.values[i]
                    break
        return self.previous

class Joystick(ColObjects.ColObj):
    def __init__(self, name, state_machine, interpolator=None, neutral=0):
        super().__init__(name)
        if not state_machine.valid:
            raise ColObjects.ColError ('**** bad sm ' + state_machine.name)
        self.state_machine = state_machine
        self.interpolator = interpolator
        self.neutral = neutral
        self.debug_limit = 4
        self.debug_count = 0
        self.previous_raw_position = 75
        self.previous_int_position = 75
        self.previous_final_position = self.neutral
    def close(self):
        super().close()
    def get(self):
        raw_position = self.state_machine.get_latest()
        try:
            int_position = int(raw_position)
        except:
            if self.debug_count < self.debug_limit:
                print ('Bad get for', self.name, raw_position)
                self.debug_count += 1
            raw_position = self.previous_raw_position
            int_position = self.previous_int_position
        self.previous_raw_position = raw_position
        self.previous_int_position = int_position
        if self.interpolator is None:
            final_position = int_position
        else:
            final_position = self.interpolator.interpolate(int_position)
            if final_position is None:
                final_position = self.previous_final_position
        self.previous_final_position = final_position
        return final_position

class Interpolator(ColObjects.ColObj):
    def __init__(self, name, keys, values):  #  arrays of matching pairs
                                        # keys ascending integers
                                        # values any floats
        super().__init__(name)
        self.keys = keys
        self.values = values
    def interpolate(self, in_key):  #  input is integer
        if in_key is None:
            return None
        below_ok = False
        above_ok = False
        for i in range(len(self.keys)):
            if in_key == self.keys[i]:
                return self.values[i]
            if in_key > self.keys[i]:
                below_key = self.keys[i]
                below_value = self.values[i]
                below_ok = True
            if in_key < self.keys[i]:
                above_key = self.keys[i]
                above_value = self.values[i]
                above_ok = True
                break
        if above_ok and below_ok:
            out_value = below_value + (((in_key - below_key) / (above_key - below_key)) * (above_value - below_value))
            return out_value
        else:
            return None

VALID_MODES = ['TANK','CAR']

class RemoteControl(ColObjects.ColObj):
    def __init__(self,
                 name,
                 left_side,
                 right_side,
                 left_up_down,
                 left_sideways,
                 right_up_down,
                 right_sideways,
                 mode_switch
                 ):
        #  Note: the gpios are GPIO CONTROL objects
        #        the sides implement fwd(speed) and rev(speed)
        super().__init__(name)
        self.left_side = left_side
        self.right_side = right_side
        self.left_up_down = left_up_down
        self.left_sideways = left_sideways
        self.right_up_down = right_up_down
        self.right_sideways = right_sideways
        self.mode_switch = mode_switch
        self.mode = 'OFF'
        keys = [-101, -50, -2, 2, 50, 101]
        values = [1.0, 1.0, 1.0, 1.0, 0.0, -1.0]
        self.left_side_interpolator = Interpolator('remls',keys, values)
        values = [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0]
        self.right_side_interpolator = Interpolator('remrs',keys, values)
        self.min_throttle = -100
        self.max_throttle = 100
        self.min_steering = -100
        self.max_steering = 100
        self.reversing_mode = 0

    def constrain(self, n, lowest, highest):
        if n > highest:
            a = highest
        elif n < lowest:
            a = lowest
        else:
            a = n
        return a
        
    def __str__(self):
        out_string = ''
        out_string += self.name
        return out_string

    def calculate_speeds_tank(self, left_value, right_value):
        left = self.constrain (left_value, self.min_throttle, self.max_throttle)
        right = self.constrain (right_value, self.min_steering, self.max_steering)
        return int(left), int(right)

    def calculate_speeds_car(self, throttle, steering):
        if ((throttle < 0) and (self.reversing_mode == 0)):
                left = self.constrain (throttle + steering, self.min_throttle, self.max_throttle)
                right = self.constrain (throttle - steering, self.min_throttle, self.max_throttle)
        else:
            right = self.constrain (throttle + steering, self.min_throttle, self.max_throttle)
            left = self.constrain (throttle - steering, self.min_throttle, self.max_throttle)
        return int(left), int(right)

    def set_mode_from_switch(self):
        if self.mode_switch == None:
            self.mode = 'CAR'
        else:
            self.mode = self.mode_switch.get()

    def calculate_speeds(self):
        self.set_mode_from_switch()
        if self.mode == 'TANK':
            left_value = self.left_up_down.get()
            right_value = self.right_up_down.get()
            return self.calculate_speeds_tank(left_value, right_value)
        elif self.mode == 'CAR':
            self.throttle_value = self.left_up_down.get()
            self.steering_value = self.right_sideways.get()
            return self.calculate_speeds_car(self.throttle_value, self.steering_value)
        else:
            return 0,0

    def drive(self):
        left_speed, right_speed = self.calculate_speeds()
        self.left_side.drive(left_speed)
        self.right_side.drive(right_speed)
        return left_speed, right_speed
    
    def stop(self):
        self.left_side.stop()
        self.right_side.stop()
        utime.sleep_ms(2)
        
    def close(self):
        self.stop()
        self.left_up_down.close()
        self.right_sideways.close()
        self.left_side.close()
        self.right_side.close()

class RemoteControlWithHeadlights(RemoteControl):
    def __init__(self,
                 name,
                 left_side,
                 right_side,
                 left_up_down,
                 left_sideways,
                 right_up_down,
                 right_sideways,
                 mode_switch,
                 left_headlight,
                 right_headlight
                 ):
        super().__init__(name, left_side, right_side,
                 left_up_down,
                 left_sideways,
                 right_up_down,
                 right_sideways,
                 mode_switch)
        self.left_headlight = left_headlight
        self.right_headlight = right_headlight

    def drive(self):
        left_speed, right_speed = self.calculate_speeds()
        if self.throttle_value < 0:
            self.left_headlight.red()
            self.right_headlight.red()
        elif self.steering_value < -10:
            self.left_headlight.on()
            self.right_headlight.off()
        elif self.steering_value > 10:
            self.left_headlight.off()
            self.right_headlight.on()
        else:
            self.left_headlight.on()
            self.right_headlight.on()
        self.left_side.drive(left_speed)
        self.right_side.drive(right_speed)
        return left_speed, right_speed

    def close(self):
        self.left_headlight.off()
        self.right_headlight.off()
        super().close()

if __name__ == "__main__":
    print (module_name)
    print ('----- GPIO C -----\n',GPIO.GPIO.str_allocated())
    sm1 = StateMachine('TEST', 'MEASURE', 4)
    print ('--- SM A -----\n',ColObjects.PIO.str_allocated())
    js = Joystick('test', sm1)
    utime.sleep_ms(10)
    print ('----- GPIO D -----\n',GPIO.GPIO.str_allocated())
    js.close()
    sm1.close()
    print ('----- GPIO E -----\n',GPIO.GPIO.str_allocated())