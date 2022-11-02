module_name = 'PicoA_v09.py'

import DriveTrainRemote_v12 as DriveTrain
import NeoPixel_v03 as NeoPixel
RemoteControl = NeoPixel.RemoteControl
GPIOPico = RemoteControl.GPIOPico
ColObjects = GPIOPico.ColObjects
import utime

class ThisLeftSide(DriveTrain.Side):

    def __init__(self):
        self.lf_speed_pin_no = 6                  # blue
        self.lf_pulse_pin_no = 7  # green
        self.lf_direction_pin_no = 8          # yellow
        self.motor_lf = GPIOPico.FIT0441Motor('Left Front', self.lf_direction_pin_no,
                                              self.lf_speed_pin_no, self.lf_pulse_pin_no)
        self.motor_lf.name = 'Left Front'

        self.lb_speed_pin_no = 21
        self.lb_pulse_pin_no = 20
        self.lb_direction_pin_no = 19
        self.motor_lb = GPIOPico.FIT0441Motor('Left Back', self.lb_direction_pin_no,
                                              self.lb_speed_pin_no, self.lb_pulse_pin_no)
        self.motor_lb.name = 'Left Back'

        self.left_motor_list = [self.motor_lf, self.motor_lb]

        super().__init__('Left Side', 'L', self.left_motor_list)

class ThisRightSide(DriveTrain.Side):

    def __init__(self):
        self.right_front_speed_pin_no = 2                 # blue
        self.right_front_pulse_pin_no = 3  # green
        self.right_front_direction_pin_no = 4          # yellow
        self.motor_right_front = GPIOPico.FIT0441Motor('Right Front', self.right_front_direction_pin_no,
                                                       self.right_front_speed_pin_no, self.right_front_pulse_pin_no)
        self.motor_right_front.name = 'Right Front'

        self.right_back_speed_pin_no = 10
        self.right_back_pulse_pin_no = 11
        self.right_back_direction_pin_no = 12
        self.motor_right_back = GPIOPico.FIT0441Motor('Right Back', self.right_back_direction_pin_no,
                                                      self.right_back_speed_pin_no, self.right_back_pulse_pin_no)
        self.motor_right_back.name = 'Right Back'

        self.right_motor_list = [self.motor_right_front, self.motor_right_back]

        super().__init__('Right Side', 'R', self.right_motor_list)

class ThisStateMachine1(RemoteControl.StateMachine):
    #  reads remote control channel 1 (right joystick sideways)
    def __init__(self):
        name = 'RC Channel 1'
        code = 'MEASURE'
        pin_no = 26
        super().__init__(name, code, pin_no)

class ThisStateMachine2(RemoteControl.StateMachine):
    #  reads remote control channel 2 (right joystick up down)
    def __init__(self):
        name = 'RC Channel 2'
        code = 'MEASURE'
        pin_no = 16
        super().__init__(name, code, pin_no)

class ThisStateMachine3(RemoteControl.StateMachine):
    #  reads remote control channel 3 (left joystick up down)
    def __init__(self):
        name = 'RC Channel 3'
        code = 'MEASURE'
        pin_no = 22
        super().__init__(name, code, pin_no)

class ThisStateMachine4(RemoteControl.StateMachine):
    #  reads remote control channel 4 (left joystick sideways)
    def __init__(self):
        name = 'RC Channel 4'
        code = 'MEASURE'
        pin_no = 17
        super().__init__(name, code, pin_no)

class ThisStateMachine5(RemoteControl.StateMachine):
    #  reads remote control channel 5 (3 position switch)
    def __init__(self):
        name = 'RC Channel 5'
        code = 'MEASURE'
        pin_no = 5
        super().__init__(name, code, pin_no)

class ThisStateMachine6(RemoteControl.StateMachine):
    #  reads remote control channel 6 (knob)
    def __init__(self):
        name = 'RC Channel 6'
        code = 'MEASURE'
        pin_no = 18
        super().__init__(name, code, pin_no)

class ThisDeadZone(RemoteControl.Interpolator):
    def __init__(self, name):
        super().__init__(name, [49, 74, 76, 101],[-100.0, 0.0, 0.0, 100.0])

class ThisLinear(RemoteControl.Interpolator):
    def __init__(self, name):
        super().__init__(name, [49, 101],[0.0, 100.0])

class ThisKnob(RemoteControl.Joystick):
    def __init__(self):
        state_machine = ThisStateMachine6()
        interpolator = ThisLinear('Knob')
        name = 'Knob 6'
        super().__init__(name, state_machine, interpolator)
    def close(self):
        self.state_machine.close()
        self.interpolator.close()
        super().close()

class ThisLeftUpDown(RemoteControl.Joystick):
    def __init__(self):
        state_machine = ThisStateMachine3()
        interpolator = ThisDeadZone('LUD')
        name = 'Left Up Down'
        super().__init__(name, state_machine, interpolator)
    def close(self):
        self.state_machine.close()
        self.interpolator.close()
        super().close()

class ThisLeftSideways(RemoteControl.Joystick):
    def __init__(self):
        state_machine = ThisStateMachine4()
        interpolator = ThisDeadZone('LS')
        name = 'Left Sideways'
        super().__init__(name, state_machine, interpolator)
    def close(self):
        self.state_machine.close()
        self.interpolator.close()
        super().close()

class ThisRightUpDown(RemoteControl.Joystick):
    def __init__(self):
        state_machine = ThisStateMachine2()
        interpolator = ThisDeadZone('RUD')
        name = 'Right Up Down'
        super().__init__(name, state_machine, interpolator)
    def close(self):
        self.state_machine.close()
        self.interpolator.close()
        super().close()

class ThisRightSideways(RemoteControl.Joystick):
    def __init__(self):
        state_machine = ThisStateMachine1()
        interpolator = ThisDeadZone('RS')
        name = 'Right Sideways'
        super().__init__(name, state_machine, interpolator)
    def close(self):
        self.state_machine.close()
        self.interpolator.close()
        super().close()

class ThisModeSwitch(RemoteControl.RCSwitch):
    def __init__(self):
        intervals = [60,80,110]
        values = ['OFF','TANK','CAR']
        name = 'Channel5'
        state_machine = ThisStateMachine5()
        super().__init__(name, state_machine, intervals, values)
    def close(self):
        self.state_machine.close()
        super().close()

class ThisRemoteControl(RemoteControl.RemoteControl):
    def __init__(self):
        left_side = ThisLeftSide()
        right_side = ThisRightSide()
        left_up_down = ThisLeftUpDown()
        left_sideways = ThisLeftSideways()
        right_up_down = ThisRightUpDown()
        right_sideways = ThisRightSideways()
        mode_switch = ThisModeSwitch()
        super().__init__('Pico A Remote Control',
                         left_side,
                         right_side,
                         left_up_down,
                         left_sideways,
                         right_up_down,
                         right_sideways,
                         mode_switch)
        

class ThisRing(NeoPixel.NeoPixel):
    def __init__(self):
        super().__init__('Test Ring', 27, 7, 'GRB')

if __name__ == "__main__":
    
    print (module_name)

    if False:
        my_switch = ThisModeSwitch()
        print (my_switch)
        utime.sleep_ms(90)
        print (my_switch.get())
        my_switch.close()

    if False:
        my_sm = ThisStateMachine3()
        v = my_sm.get_latest()
        while v is None:
            utime.sleep_ms(1)
            v = my_sm.get_latest()
        print (v)

    if False:
        my_stick = ThisLeftSideways()
        utime.sleep_ms(100)
        print (my_stick.get())

    if True:
        my_ring = ThisRing()
        my_ring.show_ring(2)
        my_remote = ThisRemoteControl()
        print (RemoteControl.StateMachine.str_allocated())
        utime.sleep_ms(500)
        my_ring.show_ring(3)
        my_remote.set_mode_from_switch()
        print (my_remote, my_remote.mode)
        print (my_remote.calculate_speeds())
        utime.sleep_ms(500)
        my_ring.show_ring(4)
        my_remote.close()
        utime.sleep_ms(500)
        my_ring.close()

