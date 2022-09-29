import PicoRobotics
import math
import utime

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

class MyDriveTrain(DriveTrain):
    
    def __init__(self):
        my_board = ThisBoard.board
        self.left_side = Side([
            KitronikMotor('FRONT_LEFT', my_board, 1, 'f', 'r'),
            KitronikMotor('REAR_LEFT', my_board, 3, 'f', 'r')])
        self.right_side = Side([
            KitronikMotor('FRONT_RIGHT', my_board, 2, 'r', 'f'),
            KitronikMotor('REAR_RIGHT', my_board, 4, 'r', 'f')])
        super().__init__(self.left_side, self.right_side)
        self.last_spin = ''

class ThisBoard():

    board = PicoRobotics.KitronikPicoRobotics()
    
    def __init__(self):
        self.name = 'KITRONIK'

ThisBoard()