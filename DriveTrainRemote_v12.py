module_name = 'DriveTrainRemote_v11.py'

#  Suitable for remote control (no smoothness) or very basic robots
#  NOTE: The lowest level objects (Motors) are in GPIO, Kitronik etc.
#        depending on how they connect

import ColObjects_v03 as ColObjects
import utime

class Side(ColObjects.ColObj):
    def __init__(self, name, orientation, motor_list):
        super().__init__(name)
        self.orientation = orientation
        if orientation not in ['L','R']:
            raise ColObjects.ColError ("Must be 'L' for left side or 'R' for right side")
        self.motor_list = motor_list
        self.min_speed = 0
        self.max_speed = 100
        
    def fwd(self, speed):
        for motor in self.motor_list:
            if self.orientation == 'L':
                motor.anti(speed)
            else:
                motor.clk(speed)

    def rev(self, speed):
        for motor in self.motor_list:
            if self.orientation == 'L':
                motor.clk(speed)
            else:
                motor.anti(speed)

    def drive(self, speed):
        if self.min_speed < speed <= self.max_speed:
            self.fwd(speed)
        elif self.min_speed < -speed <= self.max_speed:
            self.rev(-speed)
        else:
            self.stop()

    def stop(self):
        for motor in self.motor_list:
            motor.stop()
        
    def close(self):
        for motor in self.motor_list:
            motor.close()
        super().close()

class DriveTrain(ColObjects.ColObj): #  This is a basic drive train with no distance feedback
                    #  e.g. using DC motors or sailwinch servos
                    #  Distance is estimated using time
    
    def __init__(self, name, left_side, right_side):
        super().__init__(name)
        self.left_side = left_side
        self.right_side = right_side
        self.millimetre_factor = 30
        self.degree_factor = 30
        self.min_speed = 0
        self.max_speed = 100
            
    def fwd(self, speed=50, millimetres=50):
        self.left_side.fwd(speed)
        self.right_side.fwd(speed)
        if millimetres > 0:
            ms = self.convert_millimetres_to_milliseconds(millimetres, speed)
            utime.sleep_ms(ms)
            self.stop()
            return ms
        return 0

    def rev(self, speed=50, millimetres=50):
        self.left_side.rev(speed)
        self.right_side.rev(speed)
        if millimetres > 0:
            ms = self.convert_millimetres_to_milliseconds(millimetres, speed)
            utime.sleep_ms(ms)
            self.stop()
            return ms
        return 0

    def drive(self, speed, millimetres=50):
        if self.min_speed < speed <= self.max_speed:
            self.fwd(speed, millimetres)
        elif self.min_speed < -speed <= self.max_speed:
            self.rev(speed, millimetres)
        else:
            self.stop()

    def spl(self, speed=90, degrees=90):
        self.left_side.rev(speed)
        self.right_side.fwd(speed)
        if degrees > 0:
            ms = self.convert_degrees_to_milliseconds(degrees, speed)
            utime.sleep_ms(ms)
            self.stop()
            return ms
        return 0

    def spr(self, speed=90, degrees=90):
        self.left_side.fwd(speed)
        self.right_side.rev(speed)
        if degrees > 0:
            ms = self.convert_degrees_to_milliseconds(degrees, speed)
            utime.sleep_ms(ms)
            self.stop()
            return ms
        return 0

    def stop(self):
        self.left_side.stop()
        self.right_side.stop()

    def close(self):
        self.left_side.close()
        self.right_side.close()
        super().close()

    def convert_millimetres_to_milliseconds(self, millimetres, speed):
        milliseconds = int (float(millimetres) * self.millimetre_factor)
        return milliseconds

    def convert_degrees_to_milliseconds(self, millimetres, speed):
        degrees = int (float(millimetres) * self.degree_factor)
        return degrees

if __name__ == "__main__":
    print (module_name)


