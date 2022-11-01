module_name = 'RemoteControl_v08.py'

import GPIOPico_v15 as GPIOPico
ColObjects = GPIOPico.ColObjects
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

class StateMachine(ColObjects.ColObj):
    
    allocated = ['FREE']*8
    valid_codes = ['MEASURE']

    def str_allocated():
        out_string = ''
        for i in range(len(StateMachine.allocated)):
            if StateMachine.allocated[i] != 'FREE':
                obj = StateMachine.allocated[i]
                out_string += ('{:02}'.format(i) + ' : ' +
                                '{:18}'.format(obj.name) + ' : ' +
                                str(obj) + "\n")
        return out_string

    def allocate(obj):
        for i in range(len(StateMachine.allocated)):
            if StateMachine.allocated[i] == 'FREE':
                StateMachine.allocated[i] = obj
                return i
        return None

    def deallocate(no):
        StateMachine.allocated[no] == 'FREE'

    def __init__(self, name, code, pin_no, hertz=100000):
        response = super().__init__(name)
        if not self.valid:
            return None
        self.valid = False
        if code not in StateMachine.valid_codes:
            print ('**',name,'**', code, 'not in', StateMachine.valid_codes)
            return None
        self.code = code
        gpio_wanted = GPIOPico.GPIO.allocated[pin_no]
        if gpio_wanted != 'FREE':
            print ('**',name,'**', pin_no, 'in use by', gpio_wanted)
            return None
        self.pin_no = pin_no
        self.gpio = GPIOPico.ControlPin(self.name + '_control', self.pin_no)
        self.pin = self.gpio.pin
        free_sm_no = StateMachine.allocate(self)
        if free_sm_no is None:
            print ('**',name,'** no free state machine found')
            return None
        self.state_machine_no = free_sm_no
        if code != 'MEASURE':
            print ('**',name,'** code', code,'not implemented yet')
            return None
        self.instance = rp2.StateMachine(self.state_machine_no, measure, freq=hertz, in_base=self.pin, jmp_pin=self.pin)
        self.valid = True
        self.instance.active(1)
    def get_next_blocking(self):
        self.value =  self.instance.get()
        return self.value
    def get_latest(self):
        self.value = None
        while self.instance.rx_fifo():
            self.value = self.instance.get()
        return self.value
    def close(self):
        if self.valid:
            self.instance.active(0)
            StateMachine.deallocate(self.state_machine_no)
            self.gpio.close()
            super().close()

class RCSwitch(ColObjects.ColObj):
    def __init__(self, name, state_machine, intervals, values):  #  sequence of positions
        response = super().__init__(name)
        if not self.valid:
            return None
        self.intervals = intervals
        self.values = values
        self.state_machine = state_machine
        if not self.state_machine.valid:
            print ('**** bad sm', self.state_machine.name)
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
    def __init__(self, name, state_machine, interpolator):
        response = super().__init__(name)
        if not self.valid:
            return None
        self.state_machine = state_machine
        if not self.state_machine.valid:
            print ('**** bad sm', self.state_machine.name)
        self.interpolator = interpolator
        if interpolator is not None:
            self.previous = self.interpolator.interpolate(75)
        else:
            self.previous = 75  #  mid point
    def close(self):
        super().close()
    def get(self):
        value = self.state_machine.get_latest()
        if self.interpolator is not None:
            if value is not None:
                self.position = self.interpolator.interpolate(value)
                if self.position != self.previous:
                    self.previous = self.position
            return self.previous
        else:
            return value

class Interpolator(ColObjects.ColObj):
    def __init__(self, name, keys, values):  #  arrays of matching pairs
                                        # keys ascending integers
                                        # values any floats
        response = super().__init__(name)
        if not self.valid:
            return None
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
        response = super().__init__(name)
        if not self.valid:
            return None
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

    def __str__(self):
        out_string = ''
        out_string += self.name
        return out_string

    def calculate_speeds_tank(self, left_value, right_value):
        left_speed = left_value
        right_speed = right_value
        return left_speed, right_speed

    def calculate_speeds_car(self, throttle_value, steering_value):
        if ((throttle_value is None) or (steering_value is None)):
            return 0,0
        #print (self.left_side_interpolator, self.right_side_interpolator)
        left_factor = self.left_side_interpolator.interpolate(steering_value)
        right_factor = self.right_side_interpolator.interpolate(steering_value)
        #print (left_factor, right_factor, throttle_value)
        left_speed = int(throttle_value * left_factor)
        right_speed = int(throttle_value * right_factor)
        return left_speed, right_speed

    def set_mode_from_switch(self):
        if self.mode_switch == None:
            self.mode = 'TANK'
        else:
            self.mode = self.mode_switch.get()

    def calculate_speeds(self):
        self.set_mode_from_switch()
        if self.mode == 'TANK':
            left_value = self.left_up_down.get()
            right_value = self.right_up_down.get()
            return self.calculate_speeds_tank(left_value, right_value)
        elif self.mode == 'CAR':
            throttle_value = self.left_up_down.get()
            steering_value = self.right_sideways.get()
            return self.calculate_speeds_car(throttle_value, steering_value)
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
        self.left_side.close()
        self.right_side.close()

if __name__ == "__main__":
    print (module_name)
