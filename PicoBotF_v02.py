import GPIOPico_v05 as GPIO
import Kitronik_v04 as Kitronik

ThisBoard = Kitronik.PicoRobotics.KitronikPicoRobotics()

class ThisVolts(GPIO.Volts):
    def __init__(self):
        super().__init__(29, 'VIN')


class ThisHCSR04(GPIO.HCSR04):
    def __init__(self):
        super().__init__(name='FRONT_US',
                 trigger_pin_no=19,
                 echo_pin_no=20,
                 critical_distance=100.0)


class TheseIRSensors():
    def __init__(self):
        self.front_left_ir = GPIO.IRSensor(22,'FRONT_LEFT_IR')
        self.front_right_ir = GPIO.IRSensor(16,'FRONT_RIGHT_IR')
        self.rear_left_ir = GPIO.IRSensor(18,'REAR_LEFT_IR')
        self.rear_right_ir = GPIO.IRSensor(2,'REAR_RIGHT_IR')
        self.ir_list = [self.front_left_ir, self.front_right_ir, self.rear_left_ir, self.rear_right_ir]


class TheseSwitches():
    def __init__(self):
        self.DIP_1 = GPIO.Switch(13,'DIP_1')
        self.DIP_2 = GPIO.Switch(12,'DIP_2')
        self.DIP_3 = GPIO.Switch(11,'DIP_3')
        self.DIP_4 = GPIO.Switch(6,'DIP_4')
        self.switch_list = [self.DIP_1,self.DIP_2,self.DIP_3,self.DIP_4]


class TheseButtons():
    def __init__(self):
        self.yellow_button = GPIO.Button(7,'YELLOW_BUTTON')
        #   NOTE.  On this robot, the red button is hardwired to reset
        self.button_list = [self.yellow_button]


class ThisLeftHeadlight:
    def __init__(self):
        self.name = "Left Headlight"
        self.headlight = GPIO.RGBLED(GPIO.LED(10,'LEFT_RED'), GPIO.LED(14,'LEFT_GREEN'), GPIO.LED(15,'LEFT_BLUE'),'LEFT_HEADLIGHT')

class ThisRightHeadlight:
    def __init__(self):
        self.name = "Right Headlight"
        self.headlight = GPIO.RGBLED(GPIO.LED(27,'RIGHT_RED'), GPIO.LED(26,'RIGHT_GREEN'), GPIO.LED(17,'RIGHT_BLUE'),'RIGHT_HEADLIGHT')


class ThisDriveTrain(Kitronik.DriveTrain):
    def __init__(self):
        self.left_side = Kitronik.Side([
            Kitronik.KitronikMotor('FRONT_LEFT', ThisBoard, 4, 'r', 'f'),
            Kitronik.KitronikMotor('REAR_LEFT', ThisBoard, 1, 'r', 'f')])
        self.right_side = Kitronik.Side([
            Kitronik.KitronikMotor('FRONT_RIGHT', ThisBoard, 3, 'f', 'r'),
            Kitronik.KitronikMotor('REAR_RIGHT', ThisBoard, 2, 'f', 'r')])
        super().__init__(self.left_side, self.right_side)
        self.last_spin = ''
        self.millimetre_factor = 105
        self.degree_factor = 330
        self.speed_exponent = 0.5

class ThisShoulderServo(Kitronik.Servo):
    def __init__(self):
        super().__init__(name='Shoulder Servo',
                 board=ThisBoard,
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
                 board=ThisBoard,
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
        super().__init__('Front Loader', ThisBoard, shoulder_servo, bucket_servo)
    
    
#####  For testing compilation and GPIO clashes
if __name__ == "__main__":
    print ('Kitronik_v04.py')
    bucket_servo = ThisBucketServo()
    shoulder_servo = ThisShoulderServo()
    arm = ThisArm()
    drive_train = ThisDriveTrain()
    left_headlight = ThisLeftHeadlight()
    right_headlight = ThisRightHeadlight()
    buttons = TheseButtons()
    switches = TheseSwitches()
    ir_sensors = TheseIRSensors()
    hcsr04 = ThisHCSR04()
    volts = ThisVolts()
    print (volts.str_allocated())