module_name = 'DriveTrainCommands_v01.py'

#  suitable for controlling via command stream
#  Implements smoothness
#  NOTE: The lowest level objects (Motors) are in GPIO, Kitronik etc.
#        depending on how they connect

import math

class Side():
    
    def __init__(self, name, motor_list, orientation):
        self.name = name
        self.motor_list = motor_list
        self.orientation = orientation  #  'L' is left side 'R' is right
        self.speed = 0  #  percentage of full speed. 0 is stopped

    def stop(self):
        for motor in self.motor_list:
            motor.stop()
        self.speed = 0

    def fwd(self, speed):
        self.speed = speed
        for motor in self.motor_list:
            if orientation == 'L':
                motor.anti(speed)
            else:
                motor.clk(speed)

    def rev(self, speed):
        self.speed = speed
        for motor in self.motor_list:
            if orientation == 'L':
                motor.clk(speed)
            else:
                motor.anti(speed)

    def fwd(self, speed):
        self.speed = speed
        for motor in self.motor_list:
            if orientation == 'L':
                motor.anti(speed)
            else:
                motor.clk(speed)

class DriveTrain():
    
    def __init__(self, left_motor_list, right_motor_list):
        self.left_motor_list = left_motor_list
        self.right_motor_list = right_motor_list
        self.left_side = Side('Left Side', left_motor_list, 'L')
        self.right_side = Side('Right Side', right_motor_list, 'R')
        self.angle = 0
        self.speed = 0
        self.smoothness = 0
        self.max_increments = 40

    def calculate_side_speeds(angle, speed):
        if self.angle < 45:
            left_speed = self.speed
            right_speed = - int(self.speed * ((45 - self.angle) / 45))
        elif self.angle < 90:
            left_speed = self.speed
            right_speed = int(self.speed * ((self.angle - 45) / 45))
        elif self.angle < 135:
            left_speed = int(self.speed * ((135 - self.angle) / 45))
            right_speed = self.speed
        elif self.angle < 180:
            left_speed = - int(self.speed * ((self.angle - 135) / 45))
            right_speed = self.speed
        elif self.angle < 225:
            left_speed = - self.speed
            right_speed = int(self.speed * ((225 - self.angle) / 45))
        elif self.angle < 270:
            left_speed = - self.speed
            right_speed = - int(self.speed * ((self.angle - 225) / 45))
        elif self.angle < 315:
            left_speed = - int(self.speed * ((315 - self.angle) / 45))
            right_speed = - self.speed
        elif self.angle < 360:
            left_speed = int(self.speed * ((self.angle - 315) / 45))
            right_speed = - self.speed
        else:
            print ('**** bad angle *****')
            return False
        return (left_speed, right_speed)

    def drive(self, angle, speed, smoothness=0, cruise=0):
        # angle: clockwise angle from 0 (straight ahead) to 359 (slight left)
        # speed: percentage of full speed. 0 is stop. 100 is flat out
        # smoothness: milliseconds to accelerate to speed, or 0 for instant
        # cruise: milliseconds to keep going at speed, or 0 for indefinite
        self.angle = int(angle % 360)
        self.speed = int(speed % 100)
        self.smoothness = int(smoothness)
        self.cruise = int(cruise)

        if self.smoothness < self.max_increments:
            increments = int(smoothness)
        else:
            increments = self.max_increments


        if self.smoothness != 0:
            old_left_speed = self.left_side.speed
            old_right_speed = self.right_side.speed
            left_diff = float(left_speed) - old_left_speed
            right_diff = float(right_speed) - old_right_speed
            bottom = (- (increments / 2)) + 1
            top = (increments / 2) + 1
            interval = int(float(smoothness) / float(increments))
            for i in range(bottom, top):
                utime.sleep_ms(interval)
                factor = (math.sin(i / increments * math.pi)+1.0)*0.5
                mid_left_speed = old_left_speed + int(left_diff * factor)
                mid_right_speed = old_right_speed + int(right_diff * factor)
                self.left_side.set_speed(mid_left_speed)
                self.right_side.set_speed(mid_right_speed)

        self.left_side.set_speed(left_speed)
        self.right_side.set_speed(right_speed)
        
        if self.cruise != 0:
            utime.sleep_ms(self.cruise)
            self.stop()
        return True
    
    def stop(self):
        self.left_side.stop()
        self.right_side.stop()

