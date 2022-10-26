#  PicoE_v01.py

import Side_v02 as Side
import GPIOPico_v12 as GPIOPico
import RemoteControl_v04 as RemoteControl
import utime

class ThisLeftSide(Side.Side):

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

class ThisRightSide(Side.Side):

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

class ThisChannel5(RemoteControl.RCSwitch):
    def __init__(self):
        intervals = [60,80,110]
        values = ['OFF','TANK','CAR']
        name = 'Channel5'
        pin_no = 5
        super().__init__(name, pin_no, intervals, values)

class ThisLeftUpDown(RemoteControl.Joystick):
    def __init__(self):
        keys = [49, 74, 76, 101]
        values = [-100.0, 0.0, 0.0, 100.0]
        name = 'Left Up Down'
        pin_no = 22
        super().__init__(name, pin_no, keys, values)

class ThisLeftSideways(RemoteControl.Joystick):
    def __init__(self):
        keys = [49, 74, 76, 101]
        values = [-100.0, 0.0, 0.0, 100.0]
        name = 'Left Sideways'
        pin_no = 17
        super().__init__(name, pin_no, keys, values)

class ThisRightUpDown(RemoteControl.Joystick):
    def __init__(self):
        keys = [49, 74, 76, 101]
        values = [-100.0, 0.0, 0.0, 100.0]
        name = 'Right Up Down'
        pin_no = 16
        super().__init__(name, pin_no, keys, values)

class ThisRemoteControl(RemoteControl.RemoteControl):
    def __init__(self):
        left_side = ThisLeftSide()
        right_side = ThisRightSide()
        left_up_down = ThisLeftUpDown()
        left_sideways = ThisLeftSideways()
        right_up_down = ThisRightUpDown()
        super().__init__('Pico E Remote Control',
                         'TANK',
                         left_side,
                         right_side,
                         left_up_down,
                         left_sideways,
                         right_up_down)

class ThisRedLED(GPIOPico.LED):
    def __init__(self):
        super().__init__(13, 'Red')

class ThisGreenLED(GPIOPico.LED):
    def __init__(self):
        super().__init__(14, 'Green')

class ThisBlueLED(GPIOPico.LED):
    def __init__(self):
        super().__init__(15, 'Blue')

class ThisRGBLED(GPIOPico.RGBLED):
    def __init__(self):
        red = ThisRedLED()
        green = ThisGreenLED()
        blue = ThisBlueLED()
        super().__init__('RGB', red, green, blue)

if __name__ == "__main__":
    print ('PicoE_v01.py')
    
    if False:
        my_rgb = ThisRGBLED()
        my_rgb.on()
        utime.sleep_ms(1000)
        my_rgb.off()
        my_rgb.red()
        utime.sleep_ms(1000)
        my_rgb.off()
    #my_left_side = ThisLeftSide()
    #my_right_side = ThisRightSide()
    #my_left_side.close
    #my_right_side.close
    if False:
        my_remote = ThisRemoteControl()
        print (my_remote)
        my_remote.close()

    if False:
        my_switch = ThisChannel5()
        print (my_switch)
        my_switch.close()
