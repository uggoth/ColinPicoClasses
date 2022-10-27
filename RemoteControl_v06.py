#  RemoteControl_v06.py

import GPIOPico_v12 as GPIOPico
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

class StateMachine():
    
    valid_state_machine_nos = [7,6,5,4,3,2,1,0]
    valid_codes = ['MEASURE']
    allocated = {}
    
    def __init__(self, name, code, pin_no, hertz=100000):
        self.valid = False
        if code not in StateMachine.valid_codes:
            return None
        self.name = name
        self.pin_no = pin_no
        self.gpio = GPIOPico.ControlPin(self.pin_no, self.name + '_control')
        self.pin = self.gpio.pin
        self.value = None
        # print (StateMachine.allocated)
        for state_machine_no in StateMachine.valid_state_machine_nos:
            str_no = str(state_machine_no)
            if ((str_no not in StateMachine.allocated) or (StateMachine.allocated[str_no] == 'None')):
                if code == 'MEASURE':
                    self.instance = rp2.StateMachine(state_machine_no, measure, freq=hertz, in_base=self.pin, jmp_pin=self.pin)
                StateMachine.allocated[str_no] = self.name
                self.valid = True
                self.state_machine_no = state_machine_no
                self.instance.active(1)
                break
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
            str_no = str(self.state_machine_no)
            StateMachine.allocated[str_no] = 'None'
            GPIOPico.GPIO.deallocate(self.pin_no)

class RCSwitch():
    def __init__(self, name, state_machine, intervals, values):  #  sequence of positions
        self.name = name
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

class Joystick():
    def __init__(self, name, state_machine, interpolator):
        self.name = name
        self.state_machine = state_machine
        if not self.state_machine.valid:
            print ('**** bad sm', self.state_machine.name)
        self.interpolator = interpolator
        if interpolator is not None:
            self.previous = self.interpolator.interpolate(75)
        else:
            self.previous = 75  #  mid point
    def close(self):
        self.state_machine.close()
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

class Interpolator():
    def __init__(self, keys, values):  #  arrays of matching pairs
                                        # keys ascending integers
                                        # values any floats
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

class RemoteControl():
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
        self.name = name
        self.left_side = left_side
        self.right_side = right_side
        self.left_up_down = left_up_down
        self.left_sideways = left_sideways
        self.right_up_down = right_up_down
        self.right_sideways = right_sideways
        self.mode_switch = mode_switch
        self.mode = 'OFF'
        keys = [49, 62, 74, 76, 88, 100]
        values = [1.0, 1.0, 1.0, 1.0, 0.0, -1.0]
        self.left_side_interpolator = Interpolator(keys, values)
        values = [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0]
        self.right_side_interpolator = Interpolator(keys, values)

    def __str__(self):
        out_string = ''
        out_string += self.name
        return out_string

    def calculate_speeds_tank(self, left_value, right_value):
        left_speed = int(self.left_up_down.get())
        right_speed = int(self.right_up_down.get())
        return left_speed, right_speed

    def calculate_speeds_car(self, throttle_value, steering_value):
        if ((throttle_value is None) or (steering_value is None)):
            return 0,0
        left_factor = self.left_side_interpolator.interpolate(steering_value)
        right_factor = self.right_side_interpolator.interpolate(steering_value)
        raw_speed = self.left_up_down.get()
        left_speed = int(raw_speed * left_factor)
        right_speed = int(raw_speed * right_factor)
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
        self.left_side.close()
        self.right_side.close()
    
if __name__ == "__main__":

    if False:
        print ('Testing Interpolator')
        keys = [50, 60, 62, 100]
        values = [-1.0, 0.0, 0.0, 1.0]
        print (keys)
        print (values)
        dummy_interpolator2 = Interpolator(keys, values)
        for key in [45,50,55,60,61,61.9,65,70,75,80,100,105]:
            print (key, dummy_interpolator2.interpolate(key))

    if False:
        joysticks = {'left_up_down':22, 'left_sideways':17, 'right_up_down':16}
        which_joystick = 'left_sideways'
        print ('Testing State Machine', which_joystick)
        sm_1 = StateMachine(which_joystick, 'MEASURE', joysticks[which_joystick])
        previous = 999
        for i in range(10000):
            utime.sleep_ms(1)
            value = sm_1.get_latest()
            if ((value is not None) and (value != previous)):
                print (value)
                previous = value
        sm_1.close()

    if False:
        print ('Testing 3 State Machines')
        joysticks = {'left_up_down':22, 'left_sideways':17, 'right_up_down':16}
        #  NOTE: Not using channel 1
        js_2 = 'right_up_down'
        sm_2 = StateMachine(js_2, 'MEASURE', joysticks[js_2])
        js_3 = 'left_up_down'
        sm_3 = StateMachine(js_3, 'MEASURE', joysticks[js_3])
        js_4 = 'left_sideways'
        sm_4 = StateMachine(js_4, 'MEASURE', joysticks[js_4])
        previous_2 = 999
        previous_3 = 999
        previous_4 = 999
        for i in range(10000):
            utime.sleep_ms(1)
            value_2 = sm_2.get_latest()
            if ((value_2 is not None) and (value_2 != previous_2)):
                print ('2',value_2)
                previous_2 = value_2
            value_3 = sm_3.get_latest()
            if ((value_3 is not None) and (value_3 != previous_3)):
                print ('3',value_3)
                previous_3 = value_3
            value_4 = sm_4.get_latest()
            if ((value_4 is not None) and (value_4 != previous_4)):
                print ('4',value_4)
                previous_4 = value_4
        sm_2.close()
        sm_3.close()
        sm_4.close()

    if False:
        sw5 = RCSwitch('Switch 5', 5, [65,85,105], ['OFF','TANK','CAR'])
        previous = 9999
        for i in range(10000):
            utime.sleep_ms(1)
            value = sw5.get()
            if ((value is not None) and (value != previous)):
                print (value)
                previous = value
        sw5.close()

    if False:
        dummy = RemoteControl('dummy', 'RUBBISH',None, None, None, None, None)

    if False:
        name = 'RC Channel 3'
        code = 'MEASURE'
        pin_no = 22
        sm = StateMachine(name, code, pin_no)
        utime.sleep_ms(900)
        print (sm.get_latest())
        utime.sleep_ms(900)
        print (sm.get_latest())
        utime.sleep_ms(900)
        print (sm.get_latest())
        utime.sleep_ms(900)
        print (sm.get_latest())

    print ("RemoteControl_v06.py\n")
