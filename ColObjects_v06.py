module_name = 'ColObjects_v06.py'

import math
import utime

class ColError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ColObj():
    
    allocated = {}
    free_code = 'FREE'
    
    def str_allocated():
        out_string = ('{:18}'.format('NAME') +
                        '{:18}'.format('OBJECT') + '\n')
        for name in sorted(ColObj.allocated):
            if ColObj.allocated[name] != ColObj.free_code:
                obj = ColObj.allocated[name]
                out_string += ('{:18}'.format(obj.name)  +
                                str(obj) + '\n')
        return out_string
    
    def __init__(self, name):
        self.name = name
        if name in ColObj.allocated:
            if ColObj.allocated[self.name] != ColObj.free_code:
                raise ColError(name + ' already allocated')
        ColObj.allocated[self.name] = self
        
    def __str__(self):
        return self.name
    
    def close(self):
        ColObj.allocated[self.name] = ColObj.free_code


class Motor(ColObj):
    def __init__(self, name):
        super().__init__(name)
    def clk(self, speed):
        raise ColError('**** Must be overriden')
    def anti(self, speed):
        raise ColError('**** Must be overriden')
    def stop(self):
        raise ColError('**** Must be overriden')
    def close(self):
        super().close()

class Side(ColObj):
    def __init__(self, name, which_side, my_motors):
        super().__init__(name)
        self.which_side = which_side
        self.my_motors = my_motors
    def __str__(self):
        outstring = ''
        outstring += self.name + '  '
        for motor in self.my_motors:
            outstring += motor.name + '  '
    def fwd(self, speed):
        for motor in self.my_motors:
            if self.which_side == 'L':
                motor.anti(speed)
            else:
                motor.clk(speed)
    def rev(self, speed):
        for motor in self.my_motors:
            if self.which_side == 'L':
                motor.clk(speed)
            else:
                motor.anti(speed)
    def drive(self, speed):
        if speed < 0:
            self.rev(-speed)
        else:
            self.fwd(speed)
    def stop(self):
        for motor in self.my_motors:
            motor.stop()
    def close(self):
        for motor in self.my_motors:
            motor.close()
        super().close()

class DriveTrain(ColObj):
    def __init__(self, name, left_side, right_side):
        super().__init__(name)
        self.left_side = left_side
        self.right_side = right_side
        self.millimetre_factor = 30
        self.degree_factor = 30
        self.speed_exponent = 0.5          
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
    def drive(self, speed=25, angle=0):
        raise ColError(name + ' cannot yet drive')
    def stop(self):
        self.left_side.stop()
        self.right_side.stop()
    def convert_millimetres_to_milliseconds(self, millimetres, speed):
        milliseconds = int (float(millimetres * self.millimetre_factor) / math.pow(speed, self.speed_exponent))
        return milliseconds
    def convert_degrees_to_milliseconds(self, millimetres, speed):
        degrees = int (float(millimetres * self.degree_factor) / math.pow(speed, self.speed_exponent))
        return degrees


if __name__ == "__main__":
    print (module_name)
   
    