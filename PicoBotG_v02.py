import GPIOPico_v07 as GPIO
import Kitronik_v05 as Kitronik
from machine import Pin

OnboardLED = Pin(25, Pin.OUT)
ThisBoard = Kitronik.PicoRobotics.KitronikPicoRobotics()

class ThisSailWinch(Kitronik.SailWinch):
    def __init__(self):
        super().__init__("Brush Rotator",
                         ThisBoard,
                         servo_no=2,
                         max_clockwise=50,
                         max_anticlockwise=130,
                         stopped=90)

class ThisArmServo(Kitronik.Servo):
    def __init__(self):
        super().__init__('Arm Servo',
                 ThisBoard,
                 servo_no=1,
                 max_rotation=150,
                 min_rotation=30,
                 park_position=90,
                 transport_position=90)

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
        self.front_left_ir = GPIO.IRSensor(18,'FRONT_LEFT_IR')
        self.front_right_ir = GPIO.IRSensor(22,'FRONT_RIGHT_IR')
        #self.rear_left_ir = GPIO.IRSensor(18,'REAR_LEFT_IR')
        #self.rear_right_ir = GPIO.IRSensor(2,'REAR_RIGHT_IR')
        self.ir_list = [self.front_left_ir, self.front_right_ir] #, self.rear_left_ir, self.rear_right_ir]


class TheseSwitches():
    def __init__(self):
        self.DIP_1 = GPIO.Switch(13,'DIP_1')
        self.DIP_2 = GPIO.Switch(12,'DIP_2')
        self.DIP_3 = GPIO.Switch(11,'DIP_3')
        #self.DIP_4 = GPIO.Switch(6,'DIP_4')
        self.switch_list = [self.DIP_1,self.DIP_2,self.DIP_3] #,self.DIP_4]


class TheseButtons():
    def __init__(self):
        self.yellow_button = GPIO.Button(6,'YELLOW_BUTTON')
        self.red_button = GPIO.Button(7,'YELLOW_BUTTON')
        self.button_list = [self.yellow_button, self.red_button]


class ThisLeftHeadlight:
    def __init__(self):
        self.headlight = GPIO.RGBLED(GPIO.LED(10,'LEFT_RED'), GPIO.LED(14,'LEFT_GREEN'), GPIO.LED(15,'LEFT_BLUE'),'LEFT_HEADLIGHT')

class ThisRightHeadlight:
    def __init__(self):
        self.headlight = GPIO.RGBLED(GPIO.LED(27,'RIGHT_RED'), GPIO.LED(26,'RIGHT_GREEN'), GPIO.LED(17,'RIGHT_BLUE'),'RIGHT_HEADLIGHT')


class ThisDriveTrain(Kitronik.DriveTrain):
    def __init__(self, current_wheel='3482'):
        my_board = ThisBoard
        wheels = {}
        wheels['ZR'] = {'millimetre_factor':33.0, 'degree_factor':300.0, 'speed_exponent':0.5}
        wheels['3482'] = {'millimetre_factor':45.0, 'degree_factor':130.0, 'speed_exponent':0.5}
        self.left_side = Kitronik.Side([
            Kitronik.KitronikMotor('FRONT_LEFT', my_board, 3, 'f', 'r'),
            Kitronik.KitronikMotor('REAR_LEFT', my_board, 4, 'r', 'f')])
        self.right_side = Kitronik.Side([
            Kitronik.KitronikMotor('FRONT_RIGHT', my_board, 2, 'r', 'f'),
            Kitronik.KitronikMotor('REAR_RIGHT', my_board, 1, 'f', 'r')])
        super().__init__(self.left_side, self.right_side)
        self.last_spin = ''
        self.millimetre_factor = wheels[current_wheel]['millimetre_factor']
        self.degree_factor = wheels[current_wheel]['degree_factor']
        self.speed_exponent = wheels[current_wheel]['speed_exponent']

#####  For testing compilation and GPIO clashes
if __name__ == "__main__":
    print ('PicoBotG_v02.py')
    arm_servo = ThisArmServo()
    drive_train = ThisDriveTrain()
    left_headlight = ThisLeftHeadlight()
    right_headlight = ThisRightHeadlight()
    buttons = TheseButtons()
    switches = TheseSwitches()
    ir_sensors = TheseIRSensors()
    hcsr04 = ThisHCSR04()
    volts = ThisVolts()
    print (volts.str_allocated())