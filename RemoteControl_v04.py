#  RemoteControl_v01.py

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
    def get(self):
        if self.instance.rx_fifo():
            return self.instance.get()
        else:
            return None
    def close(self):
        if self.valid:
            self.instance.active(0)
            str_no = str(self.state_machine_no)
            StateMachine.allocated[str_no] = 'None'
            GPIOPico.GPIO.deallocate(self.pin_no)

class RCSwitch():
    def __init__(self, name, pin_no, intervals, values):  #  sequence of positions
        self.name = name
        self.pin_no = pin_no
        self.intervals = intervals
        self.values = values
        self.state_machine = StateMachine(self.name + '_sm', 'MEASURE', self.pin_no)
        if not self.state_machine.valid:
            print ('**** bad sm', self.state_machine.name)
        self.previous = 'OFF'
    def __str__(self):
        return self.name + ' Pin:' + str(self.pin_no)
    def close(self):
        self.state_machine.close()
    def get(self):
        self.value = self.state_machine.get()
        if self.value is not None:
            for i in range(len(self.intervals)):
                if self.value < self.intervals[i]:
                    self.previous = self.values[i]
                    break
        return self.previous

class Joystick():
    def __init__(self, name, pin_no, keys, values):  #  see Interpolator
        self.name = name
        self.pin_no = pin_no
        self.state_machine = StateMachine(self.name + '_sm', 'MEASURE', self.pin_no)
        if not self.state_machine.valid:
            print ('**** bad sm', self.state_machine.name)
        self.interpolator = Interpolator(keys, values)
        self.previous = 50
    def close(self):
        self.state_machine.close()
    def get(self):
        value = self.state_machine.get()
        if value is not None:
            self.position = self.interpolator.interpolate(value)
            if self.position != self.previous:
                self.previous = self.position
        return self.previous

class Interpolator():
    def __init__(self, keys, values):  #  arrays of matching pairs
                                        # keys ascending integers
                                        # values any floats
        self.keys = keys
        self.values = values
    def interpolate(self, in_key):  #  input is integer
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
                 mode,
                 left_side,
                 right_side,
                 left_up_down,
                 left_sideways,
                 right_up_down
                 ):
        #  Note: the gpios are GPIO CONTROL objects
        #        the sides implement fwd(speed) and rev(speed)
        self.name = name
        if mode not in VALID_MODES:
            raise ValueError("RemoteControl mode " + mode + " not in " + str(VALID_MODES))
        self.mode = mode
        self.left_side = left_side
        self.right_side = right_side

        self.left_up_down = left_up_down
        self.left_sideways = left_sideways
        self.right_up_down = right_up_down

    def __str__(self):
        out_string = ''
        out_string += self.name + ', '
        out_string += self.mode
        return out_string

    def calculate_speed_tank(self, left_value, right_value):
        left_speed = int(self.left_up_down.get())
        right_speed = int(self.right_up_down.get())
        return left_speed, right_speed

    def calculate_speed_car(self, left_value, right_value):
        return 0, 0

    def calculate_vectors(self, angle, speed):
        # angle: clockwise angle from 0 (straight ahead)
        # speed: percentage of full speed
        self.angle = int(angle % 360)
        self.speed = int(speed % 100)
        if self.angle < 45:
            left_speed = self.speed
            right_speed = - int(self.speed * ((45 - self.angle) / 45))
        elif self.angle < 90:
            left_speed = self.speed
            right_speed = int(self.speed * ((self.angle - 45) / 45))
        elif self.angle < 135:
            left_speed = int(self.speed * ((135 - self.angle) / 45))
            right_speed = self.speed
        elif self.angle < 180:
            left_speed = - int(self.speed * ((self.angle - 135) / 45))
            right_speed = self.speed
        elif self.angle < 225:
            left_speed = - self.speed
            right_speed = int(self.speed * ((225 - self.angle) / 45))
        elif self.angle < 270:
            left_speed = - self.speed
            right_speed = - int(self.speed * ((self.angle - 225) / 45))
        elif self.angle < 315:
            left_speed = - int(self.speed * ((315 - self.angle) / 45))
            right_speed = - self.speed
        elif self.angle < 360:
            left_speed = int(self.speed * ((self.angle - 315) / 45))
            right_speed = - self.speed
        else:
            left_speed = 0
            right_speed = 0
        return left_speed, right_speed
    

    def drive(self, left_value, right_value):
        if self.mode == 'TANK':
            left_speed, right_speed = self.calculate_speed_tank(left_value, right_value)
        elif self.mode == 'CAR':
            left_speed, right_speed = self.calculate_speed_car(left_value, right_value)
        else:
            print ('**** invalid mode')
        # print (left_value, left_speed, right_value, right_speed)
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
    print ("RemoteControl_v04.py\n")

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
        which_joystick = 'left_up_down'
        print ('Testing State Machine', which_joystick)
        sm_1 = StateMachine(which_joystick, 'MEASURE', joysticks[which_joystick])
        previous = 999
        for i in range(10000):
            utime.sleep_ms(1)
            value = sm_1.get()
            if ((value is not None) and (value != previous)):
                print (value)
                previous = value
        sm_1.close()

    if False:
        print ('Testing State Machines')
        joysticks = {'left_up_down':22, 'left_sideways':17, 'right_up_down':16}
        js_1 = 'left_up_down'
        sm_1 = StateMachine(js_1, 'MEASURE', joysticks[js_1])
        js_2 = 'right_up_down'
        sm_2 = StateMachine(js_2, 'MEASURE', joysticks[js_2])
        previous_1 = 999
        previous_2 = 999
        for i in range(10000):
            utime.sleep_ms(1)
            value_1 = sm_1.get()
            if ((value_1 is not None) and (value_1 != previous_1)):
                print ('1',value_1)
                previous_1 = value_1
            value_2 = sm_2.get()
            if ((value_2 is not None) and (value_2 != previous_2)):
                print ('2',value_2)
                previous_2 = value_2
        sm_1.close()
        sm_2.close()

    if False:
        joysticks = {'left_up_down':22, 'left_sideways':17, 'right_up_down':16}
        which_joystick = 'right_up_down'
        print ('Testing Joystick', which_joystick)
        pin_no = joysticks[which_joystick]
        keys = [49, 74, 76, 101]
        values = [-100.0, 0.0, 0.0, 100.0]
        js = Joystick('Testing', pin_no, keys, values)
        previous = 9999
        for i in range(10000):
            utime.sleep_ms(1)
            value = js.get()
            if ((value is not None) and (value != previous)):
                print (value)
                previous = value
        js.close()

    if True:
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
