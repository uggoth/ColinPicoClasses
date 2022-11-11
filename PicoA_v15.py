module_name = 'PicoA_v15.py'

import DriveTrainRemote_v12 as DriveTrain
import NeoPixel_v07 as NeoPixel
RemoteControl = NeoPixel.RemoteControl
GPIOPico = RemoteControl.GPIOPico
ColObjects = GPIOPico.ColObjects
import utime
import machine

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
        pin_no = 16
        super().__init__(name, code, pin_no)

class ThisStateMachine2(RemoteControl.StateMachine):
    #  reads remote control channel 2 (right joystick up down)
    def __init__(self):
        name = 'RC Channel 2'
        code = 'MEASURE'
        pin_no = 17
        super().__init__(name, code, pin_no)

class ThisStateMachine3(RemoteControl.StateMachine):
    #  reads remote control channel 3 (left joystick up down)
    def __init__(self):
        name = 'RC Channel 3'
        code = 'MEASURE'
        pin_no = 18
        super().__init__(name, code, pin_no)

class ThisStateMachine4(RemoteControl.StateMachine):
    #  reads remote control channel 4 (left joystick sideways)
    def __init__(self):
        name = 'RC Channel 4'
        code = 'MEASURE'
        pin_no = 22
        super().__init__(name, code, pin_no)

class ThisStateMachine5(RemoteControl.StateMachine):
    #  reads remote control channel 5 (3 position switch)
    def __init__(self):
        name = 'RC Channel 5'
        code = 'MEASURE'
        pin_no = 26
        super().__init__(name, code, pin_no)

class ThisStateMachine6(RemoteControl.StateMachine):
    #  reads remote control channel 6 (knob)
    def __init__(self):
        name = 'RC Channel 6'
        code = 'MEASURE'
        pin_no = 5
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
    def get(self):
        pos_raw = super().get()
        pos = int(pos_raw / 18)
        return pos

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
        

class ThisRunningLights(NeoPixel.NeoPixel):
    def __init__(self):
        super().__init__(name='headlights', pin_no=27, no_pixels=35, mode='GRB')
        self.sectors['front_right_centre'] = [0,0]
        self.sectors['front_right_rim'] = [1,6]
        self.sectors['front_left_centre'] = [7,7]
        self.sectors['front_left_rim'] = [8,13]
        self.sectors['back_left_centre'] = [14,14]
        self.sectors['back_left_rim'] = [15,20]
        self.sectors['back_right_centre'] = [21,21]
        self.sectors['back_right_rim'] = [22,27]
        self.sectors['top'] = [28,34]
        self.sectors['all'] = [0,34]
        self.sectors['left'] = [0,34]
        self.sectors['right'] = [0,34]
        self.patterns['all_on'] = ['white']
        self.flashing = False
        self.indicator_flip_flop = False
        self.blues = False
        self.on_pattern = 'undefined'
        self.off_pattern = 'undefines'
        self.mode = 'undefined'  #  off,  dipped,  full,  hazard,  blues
        self.turning = machine.Timer(period=250, mode=machine.Timer.PERIODIC, callback=self.indicate)
        self.patterns['off'] = ['off']

    def all_off(self):
        self.flashing = False
        self.fill_sector('all','off')

    def centres_off(self):
        self.flashing = False
        self.fill_sector('front_right_centre','off')
        self.fill_sector('front_left_centre','off')
        self.fill_sector('back_left_centre','off')
        self.fill_sector('back_right_centre','off')

    def centres_on(self):
        self.flashing = False
        self.fill_sector('front_right_centre','on')
        self.fill_sector('front_left_centre','on')
        self.fill_sector('back_left_centre','red')
        self.fill_sector('back_right_centre','red')
    
    def rims_off(self):
        self.fill_sector('front_right_rim','off')
        self.fill_sector('front_left_rim','off')
        self.fill_sector('back_left_rim','off')
        self.fill_sector('back_right_rim','off')
        
    def rims_on(self):
        self.fill_sector('front_right_rim','on')
        self.fill_sector('front_left_rim','on')
        self.fill_sector('back_left_rim','red')
        self.fill_sector('back_right_rim','red')
        
    def rims_orange(self):
        self.fill_sector('front_right_rim','orange')
        self.fill_sector('front_left_rim','orange')
        self.fill_sector('back_left_rim','orange')
        self.fill_sector('back_right_rim','orange')

    def blues_on(self):
        self.fill_sector('top','white')

    def blues_blue(self):
        self.fill_sector('top','blue')

    def blues_orange(self):
        self.fill_sector('top','orange')

    def blues_off(self):
        self.fill_sector('top','off')

    def indicate(self, timer_info):
        #modes are;  off,  dipped,  full,  hazard,  blues
        if not (self.flashing):
            return
        self.indicator_flip_flop = not self.indicator_flip_flop
        if self.indicator_flip_flop:
            self.rims_orange()
            if self.mode == 'blues':
                self.blues_blue()
        else:
            self.rims_off()
            self.blues_off()
        self.show()

    def indicate_left(self):
        self.indicating_left = True
        self.indicating_right = False

    def indicate_right(self):
        self.indicating_left = False
        self.indicating_right = True

    def hazards(self):
        self.indicating_left = True
        self.indicating_right = True
        self.blues = False

    def bluesntwos(self):
        self.indicating_left = True
        self.indicating_right = True
        self.blues = True

    def set_mode(self, mode):
        self.mode = mode
        if mode == 'off':
            self.all_off()
            self.flashing = False
        elif mode == 'dipped':
            self.rims_off()
            self.centres_on()
            self.blues_off()
            self.flashing = False
        elif mode == 'full':
            self.rims_on()
            self.centres_on()
            self.blues_off()
            self.flashing = False
        elif mode == 'hazard':
            self.rims_orange()
            self.centres_on()
            self.blues_off()
            self.flashing = True
        else:
            self.rims_orange()
            self.centres_on()
            self.blues_blue()
            self.flashing = True
        self.show()
            

    def stop(self):
        self.indicating_left = False
        self.indicating_right = False
        self.blues = False

    def close(self):
        self.turning.deinit()
        utime.sleep_ms(10)
        super().close()