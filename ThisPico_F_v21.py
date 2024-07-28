module_name = 'ThisPico_F_v21.py'

import RemoteControl_v25 as RemoteControl
GPIO = RemoteControl.GPIO
ColObjects = RemoteControl.ColObjects
import Kitronik_v14 as Kitronik
import NeoPixel_v11 as NeoPixel
from machine import Pin

class ThisPico():
    opened = {}
    def add(this_object):
        ThisPico.opened[this_object.name] = this_object  
    def remove(this_object):
        del ThisPico.opened[this_object.name]  
    def str_opened():
        output = ''
        for this_name in sorted(ThisPico.opened):
            output += this_name + '\n'
        return output
    def close_all():
        for this_name in ThisPico.opened:
            ThisPico.opened[this_name].close()

class ThisBuzzer(GPIO.Buzzer):
    def __init__(self):
        super().__init__('Buzzer', 21)
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisVSYS(GPIO.Volts):
    def __init__(self):
        super().__init__('VSYS',29, 3.0, 4.8)
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisHCSR04(GPIO.HCSR04):
    def __init__(self):
        super().__init__(name='Front Ultrasonic',
                 trigger_pin_no=19,
                 echo_pin_no=20,
                 critical_distance=100.0)
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class TheseIRSensors():
    def __init__(self):
        self.name = 'TheseIRSensors'
        self.front_left_ir = GPIO.IRSensor('FRONT_LEFT_IR',22)
        self.front_right_ir = GPIO.IRSensor('FRONT_RIGHT_IR',16)
        self.rear_left_ir = GPIO.IRSensor('REAR_LEFT_IR',18)
        self.rear_right_ir = GPIO.IRSensor('REAR_RIGHT_IR',2)
        self.ir_list = [self.front_left_ir, self.front_right_ir, self.rear_left_ir, self.rear_right_ir]
        ThisPico.add(self)
    def close(self):
        for ir in self.ir_list:
            ir.close()
        ThisPico.remove(self)

class TheseSwitches():
    def __init__(self):
        self.name = 'TheseSwitches'
        self.DIP_1 = GPIO.Switch('DIP_1',13)
        self.DIP_1.description = 'remote control'
        self.DIP_2 = GPIO.Switch('DIP_2',12)
        self.DIP_2.description = 'wander around'
        self.DIP_3 = GPIO.Switch('DIP_3',11)
        self.DIP_2.description = 'bucket demo'
        self.DIP_4 = GPIO.Switch('DIP_4',6)
        self.DIP_2.description = 'reverse reversing orientation'
        self.switch_list = [self.DIP_1,self.DIP_2,self.DIP_3,self.DIP_4]
        ThisPico.add(self)
    def close(self):
        for switch in self.switch_list:
            switch.close()
        ThisPico.remove(self)


class TheseButtons():
    def __init__(self):
        self.name = 'TheseButtons'
        self.yellow_button = GPIO.Button('Yellow Button',0)
        self.blue_button = GPIO.Button('Blue Button',28)
        self.button_list = [self.yellow_button,self.blue_button]
        #   NOTE.  On this robot, the red button is hardwired to reset
        ThisPico.add(self)
    def close(self):
        for button in self.button_list:
            button.close()
        ThisPico.remove(self)

class ThisLeftHeadlight(GPIO.RGBLED):
    def __init__(self):
        red_led = GPIO.LED('LEFT_RED',10)
        green_led = GPIO.LED('LEFT_GREEN',14)
        blue_led = GPIO.LED('LEFT_BLUE',15)
        super().__init__("Left Headlight", red_led, green_led, blue_led)
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisRightHeadlight(GPIO.RGBLED):
    def __init__(self):
        red_led = GPIO.LED('RIGHT_RED',27)
        green_led = GPIO.LED('RIGHT_GREEN',26)
        blue_led = GPIO.LED('RIGHT_BLUE',17)
        super().__init__("Right Headlight", red_led, green_led, blue_led)
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisDriveTrain(ColObjects.DriveTrain):
    def __init__(self, board_object):
        self.left_side = ColObjects.Side('Left Side', 'R', [
            Kitronik.KitronikMotor('FRONT_LEFT', board_object, 4),
            Kitronik.KitronikMotor('REAR_LEFT', board_object, 1)])
        self.right_side = ColObjects.Side('Right Side', 'R', [
            Kitronik.KitronikMotor('FRONT_RIGHT', board_object, 3),
            Kitronik.KitronikMotor('REAR_RIGHT', board_object, 2)])
        super().__init__('ThisDriveTrain', self.left_side, self.right_side)
        self.last_spin = ''
        self.millimetre_factor = 102
        self.degree_factor = 275
        self.speed_exponent = 0.5
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisDriveTrainWithHeadlights(ColObjects.DriveTrainWithHeadlights):
    def __init__(self, board_object, left_headlight, right_headlight):
        self.board_object = board_object
        self.left_headlight = left_headlight
        self.right_headlight = right_headlight
        self.left_side = ColObjects.Side('Left Side', 'R', [
            Kitronik.KitronikMotor('FRONT_LEFT', board_object, 4),
            Kitronik.KitronikMotor('REAR_LEFT', board_object, 1)])
        self.right_side = ColObjects.Side('Right Side', 'R', [
            Kitronik.KitronikMotor('FRONT_RIGHT', board_object, 3),
            Kitronik.KitronikMotor('REAR_RIGHT', board_object, 2)])
        super().__init__('ThisDriveTrain', self.left_side, self.right_side, self.left_headlight, self.right_headlight)
        self.last_spin = ''
        self.millimetre_factor = 102
        self.degree_factor = 275
        self.speed_exponent = 0.5
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisShoulderServo(Kitronik.Servo):
    def __init__(self, board_object):
        super().__init__('Shoulder Servo',
                 board_object,
                 servo_no=6,
                 max_rotation=170,
                 min_rotation=50)
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()
    

class ThisBucketServo(Kitronik.Servo):
    def __init__(self, board_object):
        super().__init__('Bucket Servo',
                 board_object,
                 servo_no=7,
                 max_rotation=150,
                 min_rotation=0)
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisArm(Kitronik.Arm):
    def __init__(self, board_object):
        bucket_servo = ThisBucketServo(board_object)
        shoulder_servo = ThisShoulderServo(board_object)
        super().__init__('Front Loader', board_object, shoulder_servo, bucket_servo)
        my_arm = self
        my_arm.poses['PARK'] = [[my_arm.shoulder_servo,90],[my_arm.bucket_servo,30]]
        my_arm.poses['DUMP'] = [[my_arm.shoulder_servo,90],[my_arm.bucket_servo,100]]
        my_arm.poses['DOWN'] = [[my_arm.shoulder_servo,160],[my_arm.bucket_servo,30]]
        my_arm.poses['SCOOP'] = [[my_arm.shoulder_servo,170],[my_arm.bucket_servo,0]]
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisInterpolator(RemoteControl.Interpolator):
    def __init__(self):
        name = 'Standard Interpolator'
        keys = [48, 60, 62, 102]
        values = [-100.0, 0.0, 0.0, 100.0]
        super().__init__(name, keys, values)
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisThrottle(RemoteControl.Joystick):
    def __init__(self):
        self.tsm = RemoteControl.StateMachine(name='Throttle SM', code='MEASURE', pin_no=5)
        self.interpolator = RemoteControl.Interpolator('Throttle Interpolator', [0, 50, 70, 72, 92, 999], [-100.0, -100.0, 0.0, 0.0, 100.0, 100.0])
        super().__init__(name='Throttle', state_machine=self.tsm, interpolator=self.interpolator)
        ThisPico.add(self)
    def close(self):
        self.tsm.close()
        self.interpolator.close()
        ThisPico.remove(self)
        super().close()



class ThisAileron(RemoteControl.Joystick):
    def __init__(self):
        self.tsm = RemoteControl.StateMachine(name='Aileron SM', code='MEASURE', pin_no=3)
        self.interpolator = RemoteControl.Interpolator('Steering Interpolator', [0, 60, 78, 80, 98, 999], [100.0, 100.0, 0.0, 0.0, -100.0, -100.0])
        super().__init__(name='Aileron', state_machine=self.tsm, interpolator=self.interpolator)
        ThisPico.add(self)
    def close(self):
        self.tsm.close()
        self.interpolator.close()
        ThisPico.remove(self)
        super().close()

class ThisFlap(RemoteControl.Joystick):
    def __init__(self):
        self.tsm = RemoteControl.StateMachine(name='Flap SM', code='MEASURE', pin_no=4)
        self.interpolator = RemoteControl.Interpolator('Knob Interpolator', [0, 50, 72, 75, 97, 999], [-100.0, -100.0, 0.0, 0.0, 100.0, 100.0])
        super().__init__(name='Flap', state_machine=self.tsm, interpolator=self.interpolator)
        ThisPico.add(self)
    def close(self):
        self.tsm.close()
        self.interpolator.close()
        ThisPico.remove(self)
        super().close()

class ThisRemoteControl(RemoteControl.RemoteControl):
    def __init__(self, drive_train):
        left_side = drive_train.left_side
        right_side = drive_train.right_side
        # NOTE: Interpolation values are set experimentally with test_18_A_radio_control_v02.py
        int_t = RemoteControl.Interpolator('Throttle Interpolator', [40, 50, 70, 73, 96, 110], [-100.0, -100.0, 0.0, 0.0, 100.0, 100.0])
        int_s = RemoteControl.Interpolator('Steering Interpolator', [40, 56, 74, 76, 93, 110], [100.0, 100.0, 0.0, 0.0, -100.0, -100.0])
        int_k = RemoteControl.Interpolator('Knob Interpolator', [40, 50, 74, 76, 101, 110], [-100.0, -100.0, 0.0, 0.0, 100.0, 100.0])
        left_up_down = ThisThrottle(int_t)
        left_sideways=None
        right_up_down=None
        right_sideways = ThisAileron(int_s)
        self.knob = ThisFlap(int_k)
        mode_switch=None
        super().__init__(
                 'PicoF Remote',
                 left_side,
                 right_side,
                 left_up_down,
                 left_sideways,
                 right_up_down,
                 right_sideways,
                 mode_switch,
                 )
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisRemoteControlWithHeadlights(RemoteControl.RemoteControlWithHeadlights):
    def __init__(self, drive_train):
        self.drive_train = drive_train
        self.left_headlight = self.drive_train.left_headlight
        self.right_headlight = self.drive_train.right_headlight
        left_side = self.drive_train.left_side
        right_side = self.drive_train.right_side
        left_up_down = ThisThrottle()
        left_sideways=None
        right_up_down=None
        right_sideways = ThisAileron()
        self.kick_switch = ThisFlap()
        mode_switch=None
        super().__init__(
                 'PicoF Remote',
                 left_side,
                 right_side,
                 left_up_down,
                 left_sideways,
                 right_up_down,
                 right_sideways,
                 mode_switch,
                 self.left_headlight,
                 self.right_headlight
                 )
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

class ThisStrip(NeoPixel.NeoPixel):
    def __init__(self):
        super().__init__(name='My Strip', pin_no=7, no_pixels=4, mode='GRB')
        ThisPico.add(self)
    def close(self):
        ThisPico.remove(self)
        super().close()

#uart_tx = GPIO.Reserved('UART TX', 'OUTPUT', 0)
#uart_rx = GPIO.Reserved('UART RX', 'INPUT', 1)
smps_mode = GPIO.Reserved('SMPS Mode', 'OUTPUT', 23)
vbus_monitor = GPIO.Reserved('VBUS Monitor','INPUT',24)
onboard_led = GPIO.LED('Onboard LED', 25)
    
#####  For testing compilation and GPIO clashes
if __name__ == "__main__":
    print (module_name, '\n')
    board_object = Kitronik.Kitronik('The Only Board')
    #bucket_servo = ThisBucketServo()
    #shoulder_servo = ThisShoulderServo()
    #buzzer = ThisBuzzer()
    #arm = ThisArm(board_object)
    left_headlight = ThisLeftHeadlight()
    right_headlight = ThisRightHeadlight()
    print ('----- GPIO A -----\n',GPIO.GPIO.str_allocated())
    drive_train = ThisDriveTrainWithHeadlights(board_object,left_headlight,right_headlight)
    print ('----- GPIO B -----\n',GPIO.GPIO.str_allocated())
    my_remote = ThisRemoteControlWithHeadlights(drive_train)
    print ('----- GPIO C -----\n',GPIO.GPIO.str_allocated())
    #buttons = TheseButtons()
    #switches = TheseSwitches()
    #ir_sensors = TheseIRSensors()
    #hcsr04 = ThisHCSR04()
    #throttle = ThisThrottle()
    #steering = ThisAileron()
    #print ('----- GPIO pin allocations -----')
    #print (GPIO.GPIO.str_allocated())
    #print ('----- Kitronik servo allocations -----')
    #print (board_object.str_servo_list())
    #print ('----- Kitronik motor allocations -----')
    #print (board_object.str_motor_list())
    #print ('----- These Objects Before Close-----')
    #print (ThisPico.str_opened())
    ThisPico.close_all()
    #board_object.close()
    #print ('----- These Objects After Close-----')
    #print (ThisPico.str_opened())
    print ("----- GPIO K -----\n\r",GPIO.GPIO.str_allocated())
