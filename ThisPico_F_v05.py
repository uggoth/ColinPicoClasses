import GPIOPico_v20 as GPIO
import Kitronik_v06 as Kitronik
from machine import Pin

module_name = 'ThisPico_F_v04.py'

this_board = Kitronik.PicoRobotics.KitronikPicoRobotics()

class ThisVolts(GPIO.Volts):
    def __init__(self):
        super().__init__('VIN',29)


class ThisHCSR04(GPIO.HCSR04):
    def __init__(self):
        super().__init__(name='FRONT_US',
                 trigger_pin_no=19,
                 echo_pin_no=20,
                 critical_distance=100.0)


class TheseIRSensors():
    def __init__(self):
        self.front_left_ir = GPIO.IRSensor('FRONT_LEFT_IR',22)
        self.front_right_ir = GPIO.IRSensor('FRONT_RIGHT_IR',16)
        self.rear_left_ir = GPIO.IRSensor('REAR_LEFT_IR',18)
        self.rear_right_ir = GPIO.IRSensor('REAR_RIGHT_IR',2)
        self.ir_list = [self.front_left_ir, self.front_right_ir, self.rear_left_ir, self.rear_right_ir]


class TheseSwitches():
    def __init__(self):
        self.DIP_1 = GPIO.Switch('DIP_1',13)
        self.DIP_2 = GPIO.Switch('DIP_2',12)
        self.DIP_3 = GPIO.Switch('DIP_3',11)
        self.DIP_4 = GPIO.Switch('DIP_4',6)
        self.switch_list = [self.DIP_1,self.DIP_2,self.DIP_3,self.DIP_4]


class TheseButtons():
    def __init__(self):
        self.yellow_button = GPIO.Button('YELLOW_BUTTON',7)
        #   NOTE.  On this robot, the red button is hardwired to reset


class ThisLeftHeadlight:
    def __init__(self):
        self.name = "Left Headlight"
        self.headlight = GPIO.RGBLED('LEFT_HEADLIGHT',
                                     GPIO.LED('LEFT_RED',10),
                                     GPIO.LED('LEFT_GREEN',14),
                                     GPIO.LED('LEFT_BLUE',15))

class ThisRightHeadlight:
    def __init__(self):
        self.name = "Right Headlight"
        self.headlight = GPIO.RGBLED('RIGHT_HEADLIGHT',
                                     GPIO.LED('RIGHT_RED',27),
                                     GPIO.LED('RIGHT_GREEN',26),
                                     GPIO.LED('RIGHT_BLUE',17))


class ThisDriveTrain(Kitronik.DriveTrain):
    def __init__(self):
        self.left_side = Kitronik.Side('Left Side', [
            Kitronik.KitronikMotor('FRONT_LEFT', this_board, 4, 'r', 'f'),
            Kitronik.KitronikMotor('REAR_LEFT', this_board, 1, 'r', 'f')])
        self.right_side = Kitronik.Side('Right Side', [
            Kitronik.KitronikMotor('FRONT_RIGHT', this_board, 3, 'f', 'r'),
            Kitronik.KitronikMotor('REAR_RIGHT', this_board, 2, 'f', 'r')])
        super().__init__('ThisDriveTrain', self.left_side, self.right_side)
        self.last_spin = ''
        self.millimetre_factor = 102
        self.degree_factor = 275
        self.speed_exponent = 0.5

class ThisShoulderServo(Kitronik.Servo):
    def __init__(self):
        super().__init__(name='Shoulder Servo',
                 board=this_board,
                 servo_no=1,
                 max_rotation=180,
                 min_rotation=0,
                 park_position=90,
                 transport_position=90)
    def up(self, speed=25):
        self.move_to(new_position=90, speed=speed)
    def down(self, speed=25):
        self.move_to(new_position=159, speed=speed)
    

class ThisBucketServo(Kitronik.Servo):
    def __init__(self):
        super().__init__(name='Bucket Servo',
                 board=this_board,
                 servo_no=2,
                 max_rotation=180,
                 min_rotation=0,
                 park_position=90,
                 transport_position=90)
    def up(self, speed=25):
        self.move_to(new_position=130, speed=speed)
    def down(self, speed=25):
        self.move_to(new_position=155, speed=speed)

class ThisArm(Kitronik.Arm):
    def __init__(self):
        bucket_servo = ThisBucketServo()
        shoulder_servo = ThisShoulderServo()
        super().__init__('Front Loader', this_board, shoulder_servo, bucket_servo)
        my_arm = self
        my_arm.poses['PARK'] = [[my_arm.shoulder_servo,90],[my_arm.bucket_servo,90]]
        my_arm.poses['UP'] = [[my_arm.shoulder_servo,100],[my_arm.bucket_servo,110]]
        my_arm.poses['DUMP'] = [[my_arm.shoulder_servo,90],[my_arm.bucket_servo,155]]
        my_arm.poses['CARRY'] = [[my_arm.shoulder_servo,70],[my_arm.bucket_servo,1]]
        my_arm.poses['DOWN'] = [[my_arm.shoulder_servo,165],[my_arm.bucket_servo,10]]
        my_arm.poses['SCOOP'] = [[my_arm.shoulder_servo,160],[my_arm.bucket_servo,1]]
    
uart_tx = GPIO.Reserved('UART TX', 'OUTPUT', 0)
uart_rx = GPIO.Reserved('UART RX', 'INPUT', 1)
smps_mode = GPIO.Reserved('SMPS Mode', 'OUTPUT', 23)
vbus_monitor = GPIO.Reserved('VBUS Monitor','INPUT',24)
onboard_led = GPIO.LED('Onboard LED', 25)
onboard_volts = GPIO.Volts('Onboard Voltmeter', 29)
    
#####  For testing compilation and GPIO clashes
if __name__ == "__main__":
    print (module_name, '\n')
    #bucket_servo = ThisBucketServo()
    #shoulder_servo = ThisShoulderServo()
    arm = ThisArm()
    drive_train = ThisDriveTrain()
    left_headlight = ThisLeftHeadlight()
    right_headlight = ThisRightHeadlight()
    buttons = TheseButtons()
    switches = TheseSwitches()
    ir_sensors = TheseIRSensors()
    hcsr04 = ThisHCSR04()
    print ('----- GPIO pin allocations -----')
    print (GPIO.GPIO.str_allocated())
    print ('----- Kitronik servo allocations -----')
    print (Kitronik.str_servo_list())
    print ('----- Kitronik motor allocations -----')
    print (Kitronik.str_motor_list())
