import PicoRobotics
import math
import utime

class Servo():
    
    def __init__(self,
                 name,
                 board,
                 servo_no,
                 max_rotation,
                 min_rotation,
                 park_position,
                 transport_position):
        self.name = name
        self.board = board
        self.servo_no = servo_no
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

class Arm():
    
    steps = 20
    duration = 2.0
    
    def __init__(self, name, board, shoulder_servo, bucket_servo):
        self.board = board
        self.name = name
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


class Motor():    
    def __init__(self, name):
        self.name = name
        self.max_speed = 100  #  as an integer percentage
        self.min_speed = 0
        self.speed = self.min_speed
        self.clockwise = 'c'  #  looking at the wheel
        self.anticlockwise = 'a'
        self.rotation = self.clockwise

    def set_speed(self, speed):
        if speed > self.max_speed:
            speed = self.max_speed
        if speed < self.min_speed:
            speed = self.min_speed
        self.speed = speed
        
#    def set_direction(self, direction):
#        if direction in [self.clockwise, self.anticlockwise]:
#            self.direction = direction
        
    def set_rotation(self, rotation):
        if rotation in [self.clockwise, self.anticlockwise]:
            self.rotation = rotation
       
    def stop(self):  #  OVERRIDE
        self.speed = self.min_speed


class KitronikMotor(Motor):  
    def __init__(self, name, board, motor_no, clockwise_code, anticlockwise_code):
        super().__init__(name)
        self.board = board
        self.motor_no = motor_no
        self.clockwise_code = clockwise_code
        self.anticlockwise_code = anticlockwise_code
        self.rotation_conversion = {'c':self.clockwise_code, 'a':anticlockwise_code}

    def move(self, speed, rotation):
        self.set_speed(speed)
        self.set_rotation(rotation)
        direction = self.rotation_conversion[self.rotation]
        self.board.motorOn(self.motor_no, direction, self.speed)

    def stop(self):  #  OVERRIDING
        self.board.motorOff(self.motor_no)


class Side():
    def __init__(self, motor_list):
        self.motor_list = motor_list
        
    def move(self, speed, rotation):
        for motor in self.motor_list:
            motor.move(speed, rotation)
    
    def stop(self):
        for motor in self.motor_list:
            motor.stop()
        
class DriveTrain():
    
    def __init__(self, left_side, right_side):
        self.left_side = left_side
        self.right_side = right_side
        self.millimetre_factor = 30
        self.degree_factor = 30
        self.speed_exponent = 0.5
            
    def fwd(self, speed=50, millimetres=50):
        self.left_side.move(speed, 'a')
        self.right_side.move(speed, 'c')
        if millimetres > 0:
            ms = self.convert_millimetres_to_milliseconds(millimetres, speed)
            utime.sleep_ms(ms)
            self.stop()
            return ms
        return 0

    def rev(self, speed=50, millimetres=50):
        self.left_side.move(speed, 'c')
        self.right_side.move(speed, 'a')
        if millimetres > 0:
            ms = self.convert_millimetres_to_milliseconds(millimetres, speed)
            utime.sleep_ms(ms)
            self.stop()
            return ms
        return 0

    def spl(self, speed=90, degrees=90):
        self.left_side.move(speed, 'c')
        self.right_side.move(speed, 'c')
        if degrees > 0:
            ms = self.convert_degrees_to_milliseconds(degrees, speed)
            utime.sleep_ms(ms)
            self.stop()
            return ms
        return 0

    def spr(self, speed=90, degrees=90):
        self.left_side.move(speed, 'a')
        self.right_side.move(speed, 'a')
        if degrees > 0:
            ms = self.convert_degrees_to_milliseconds(degrees, speed)
            utime.sleep_ms(ms)
            self.stop()
            return ms
        return 0

    def stop(self):
        self.left_side.stop()
        self.right_side.stop()

    def convert_millimetres_to_milliseconds(self, millimetres, speed):
        milliseconds = int (float(millimetres * self.millimetre_factor) / math.pow(speed, self.speed_exponent))
        return milliseconds

    def convert_degrees_to_milliseconds(self, millimetres, speed):
        degrees = int (float(millimetres * self.degree_factor) / math.pow(speed, self.speed_exponent))
        return degrees

class TypicalKitronikServo(Servo):
    def __init__(self, my_board, servo_no=1):
        super().__init__(name='Typical Servo',
                 board=my_board,
                 servo_no=servo_no,
                 max_rotation=180,
                 min_rotation=0,
                 park_position=90,
                 transport_position=90)
    def up(self, speed=25):
        self.move_to(new_position=90, speed=speed)
    def down(self, speed=25):
        self.move_to(new_position=159, speed=speed)

#####  For testing compilation
if __name__ == "__main__":
    print ('Kitronik_v04.py')
    test_board = PicoRobotics.KitronikPicoRobotics()
    shoulder_servo = TypicalKitronikServo(test_board, 1)
    bucket_servo = TypicalKitronikServo(test_board, 2)
    test_arm = Arm('Front Loader', test_board, shoulder_servo, bucket_servo)