module_name = 'PicoE_v08.py'

import DriveTrainRemote_v10 as DriveTrainRemote
import RemoteControl_v08 as RemoteControl
import GPIOPico_v14 as GPIOPico
utime = RemoteControl.utime

class ThisDriveTrain(DriveTrainRemote.DriveTrain):
    def __init__(self):
        front_right = GPIOPico.L298NMotor('Front Right', clk_pin_no=14, anti_pin_no=15)
        back_right = GPIOPico.L298NMotor('Back Right',  clk_pin_no=12, anti_pin_no=13)
        front_left = GPIOPico.L298NMotor('Front Left',  clk_pin_no=19, anti_pin_no=18)
        back_left = GPIOPico.L298NMotor('Back Left', clk_pin_no=17, anti_pin_no=16)
        left_side = DriveTrainRemote.Side('Left Side','L',[front_left, back_left])
        right_side = DriveTrainRemote.Side('Right Side','R',[front_right, back_right])
        name = 'This Drive Train'
        super().__init__(name, left_side, right_side)

class ThisStateMachine1(RemoteControl.StateMachine):
    #  reads remote control channel 1 (right joystick sideways)
    def __init__(self):
        name = 'RC Channel 1'
        code = 'MEASURE'
        pin_no = 7
        super().__init__(name, code, pin_no)

class ThisStateMachine2(RemoteControl.StateMachine):
    #  reads remote control channel 2 (right joystick up down)
    def __init__(self):
        name = 'RC Channel 2'
        code = 'MEASURE'
        pin_no = 6
        super().__init__(name, code, pin_no)

class ThisRightSideways(RemoteControl.Joystick):
    def __init__(self):
        state_machine = ThisStateMachine1()
        interpolator = RemoteControl.Interpolator('RS Int',[49, 74, 76, 101],[-100.0, 0.0, 0.0, 100.0])
        name = 'Right Sideways'
        super().__init__(name, state_machine, interpolator)

class ThisRightUpDown(RemoteControl.Joystick):
    def __init__(self):
        state_machine = ThisStateMachine2()
        interpolator = RemoteControl.Interpolator('RUD Int', [49, 74, 76, 101],[-100.0, 0.0, 0.0, 100.0])
        name = 'Right Up Down'
        super().__init__(name, state_machine, interpolator)

if __name__ == "__main__":
    print (module_name)

