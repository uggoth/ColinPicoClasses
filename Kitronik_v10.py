module_name = 'Kitronik_v10.py'

import GPIOPico_v23 as GPIO
ColObjects = GPIO.ColObjects
import PicoRobotics
import math
import utime

class Kitronik(ColObjects.ColObj):
    allocated = False
    def __init__(self, name):
        if Kitronik.allocated:
            raise ColObjects.ColError('Can only have one Kitronik instance')
        Kitronik.allocated = True
        super().__init__(name)
        self.board = PicoRobotics.KitronikPicoRobotics()
        self.sda = GPIO.Reserved('Kitronik SDA', 'CONTROL', 8)
        self.scl = GPIO.Reserved('Kitronik SCL', 'CONTROL', 9)
        self.last_servo = 8
        self.free_code = '--FREE--'
        self.servo_list = [self.free_code]*(self.last_servo + 1)
        self.servo_list[0] = 'NOT_USED'
        self.last_motor = 4
        self.motor_list = [self.free_code]*(self.last_motor + 1)
        self.motor_list[0] = 'NOT_USED'
    def str_servo_list(self):
        output = ''
        for i in range(1,len(self.servo_list)):
            output += str(i) + '  ' + self.servo_list[i] + '\n'
        return output
    def str_motor_list(self):
        output = ''
        for i in range(1,len(self.motor_list)):
            output += str(i) + '  ' + self.motor_list[i] + '\n'
        return output
    def close(self):
        self.sda.close()
        self.scl.close()
        self.board.swReset()
        Kitronik.allocated = False
    def allocate_servo(self, servo_no, name):
        if self.servo_list[servo_no] != self.free_code:
            raise ColObjects.ColError('servo no {} not free for {}'.format(servo_no, name))
        self.servo_list[servo_no] = name
    def allocate_motor(self, motor_no, name):
        if self.motor_list[motor_no] != self.free_code:
            raise ColObjects.ColError('motor no {} not free for {}'.format(motor_no, name))
        self.motor_list[motor_no] = name
    def deallocate_servo(self, servo_no):
        self.servo_list[servo_no] = self.free_code
    def deallocate_motor(self, motor_no):
        self.motor_list[motor_no] = self.free_code

class SailWinch(ColObjects.ColObj):
    def __init__(self, name, board_obect, servo_no, max_clockwise, max_anticlockwise, stopped):
        super().__init__(name)
        board_object.allocate_servo(servo_no, name)
        self.board_object = board_object
        self.board = board_object.board
        self.servo_no = int(servo_no)
        self.max_clockwise = int(max_clockwise)
        self.max_anticlockwise = int(max_anticlockwise)
        self.stopped = int(stopped)
    def set_speed(self, speed):  #  -100 is full anticlockwise, +100 is clockwise, 0 is stopped
        speed = int(speed)
        if (abs(speed) > 100):
            return False
        if speed == 0:
            self.board.servoWrite(self.servo_no, self.stopped)
        else:
            crange = self.max_clockwise - self.stopped
            pos = self.stopped + int(crange * speed / 100)
            self.board.servoWrite(self.servo_no, pos)
    def close(self):
        self.board_object.deallocate_servo(servo_no)
        super().close()

class Servo(ColObjects.ColObj):   
    def __init__(self,
                 name,
                 board_object,
                 servo_no,
                 max_rotation,
                 min_rotation,
                 park_position,
                 transport_position):
        super().__init__(name)
        self.board_object = board_object
        self.board_object.allocate_servo(servo_no, name)
        self.board = board_object.board
        self.servo_no = int(servo_no)
        self.max_rotation = max_rotation
        self.min_rotation = min_rotation
        self.park_position = park_position
        self.transport_position = transport_position
        self.current_position = self.park_position
        self.start_position = self.current_position
        self.target_position = self.current_position
    def park(self):
        self.move_to(self.park_position)
    def transport(self):
        self.move_to(self.transport_position)
    def move_to(self, new_position, speed=50):     # speed is from 1 to 100
        delay = int(1000 / speed)
        rotation = new_position - self.current_position
        no_increments = int(math.fabs(rotation) / 3)
        if no_increments < 1:
            return
        increment = rotation / no_increments
        for i  in range(no_increments):
            self.board.servoWrite(self.servo_no, self.current_position + (increment * i))
            utime.sleep_ms(delay)
        self.board.servoWrite(self.servo_no, new_position)
        self.current_position = new_position
    def close(self):
        self.board_object.deallocate_servo(self.servo_no)
        super().close()

class TypicalKitronikServo(Servo):
    def __init__(self, my_board, servo_no=1):
        super().__init__(name='Typical Servo',
                 board_object=my_board,
                 servo_no=servo_no,
                 max_rotation=180,
                 min_rotation=0,
                 park_position=90,
                 transport_position=90)
    def up(self, speed=25):
        self.move_to(new_position=90, speed=speed)
    def down(self, speed=25):
        self.move_to(new_position=159, speed=speed)


class Arm(ColObjects.ColObj):
    
    steps = 20
    duration = 2.0
    
    def __init__(self, name, board_object, shoulder_servo, bucket_servo):
        super().__init__(name)
        self.board_object = board_object
        self.board = self.board_object.board
        self.shoulder_servo = shoulder_servo
        self.bucket_servo = bucket_servo
        self.poses = {}
        self.poses['PARK'] = [[self.shoulder_servo,90],[self.bucket_servo,90]]
        self.poses['UP'] = [[self.shoulder_servo,100],[self.bucket_servo,110]]
        self.poses['DOWN'] = [[self.shoulder_servo,120],[self.bucket_servo,130]]
    
    def do_pose(self, pose_id, speed=50):  #  from 1 to 100
        this_pose = self.poses[pose_id]
        nservos = len(this_pose)
        interval_ms = int((Arm.duration / float(speed)) * 1000.0)
        for j in range(nservos):
            servo = this_pose[j][0]
            target = this_pose[j][1]
            servo.start_position = servo.current_position
            servo.target_position = target
        for i in range(Arm.steps):
            for j in range(nservos):
                servo = this_pose[j][0]
                target = servo.target_position
                start = servo.start_position
                new_position = start + ((float(target - start) / Arm.steps) * i)
                self.board.servoWrite(servo.servo_no, new_position)
                utime.sleep_ms(interval_ms)
        for j in range(nservos):
            servo = this_pose[j][0]
            self.board.servoWrite(servo.servo_no, servo.target_position)
            servo.current_position = servo.target_position
    def close(self):
        self.shoulder_servo.close()
        self.bucket_servo.close()

class KitronikMotor(ColObjects.Motor):  
    def __init__(self, name, board_object, motor_no):
        super().__init__(name)
        self.board_object = board_object
        self.board_object.allocate_motor(motor_no, name)
        self.board = board_object.board
        self.max_speed = 100  #  as an integer percentage
        self.min_speed = 0
        self.motor_no = motor_no
    def clk(self, speed):
        self.board.motorOn(self.motor_no, 'f', speed)
    def anti(self, speed):
        self.board.motorOn(self.motor_no, 'r', speed)
    def stop(self):
        self.board.motorOff(self.motor_no)
    def close(self):
        self.board_object.deallocate_motor(self.motor_no)
        super().close()

#####  For testing compilation
if __name__ == "__main__":
    print (module_name)
    board_object = Kitronik('The Only Board')
    test_sailwinch = SailWinch('TestSailWinch', board_object, 3, 99, 99, 99)
    shoulder_servo = TypicalKitronikServo(board_object, 1)
    #bad_sailwinch = SailWinch('BadSailWinch', board, 2, 99, 99, 99)
    print ('SERVO LIST:')
    print (board_object.str_servo_list())
    test_arm = Arm('Front Loader', board_object, shoulder_servo, shoulder_servo)
    test_motor = KitronikMotor('tmotor', board_object, 1)
    #bad_motor = KitronikMotor('tmotor', board, 2)
    print ('MOTOR LIST BEFORE CLOSE:')
    print (board_object.str_motor_list())
    test_motor.close()
    print ('MOTOR LIST AFTER CLOSE:')
    print (board_object.str_motor_list())
