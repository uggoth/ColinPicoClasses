module_name = 'ColObjects_v08.py'

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

class Interpolator(ColObj):
    def __init__(self, name, keys, values): # arrays of matching pairs
                                            # keys ascending integers
                                            # values any floats
        super().__init__(name)
        self.keys = keys
        self.values = values
    def interpolate(self, in_key):  #  input is integer
        if in_key is None:
            return None
        below_ok = False
        above_ok = False
        for i in range(len(self.keys)):
            if in_key == self.keys[i]:
                return self.values[i]
            if in_key > self.keys[i]:
                below_key = self.keys[i]
                below_value = self.values[i]
                below_ok = True
            if in_key < self.keys[i]:
                above_key = self.keys[i]
                above_value = self.values[i]
                above_ok = True
                break
        if above_ok and below_ok:
            out_value = below_value + (((in_key - below_key) / (above_key - below_key)) * (above_value - below_value))
            return out_value
        else:
            return None


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
        keys = [-101, -50, -2, 2, 50, 101]
        values = [1.0, 1.0, 1.0, 1.0, 0.0, -1.0]
        self.left_side_interpolator = Interpolator(name+'_remls',keys, values)
        values = [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0]
        self.right_side_interpolator = Interpolator(name+'_remrs',keys, values)
    def calculate_speeds_car(self, throttle_value, steering_value):
        if ((throttle_value is None) or (steering_value is None)):
            return 0,0
        left_factor = self.left_side_interpolator.interpolate(steering_value)
        right_factor = self.right_side_interpolator.interpolate(steering_value)
        left_speed = int(throttle_value * left_factor)
        right_speed = int(throttle_value * right_factor)
        return left_speed, right_speed
    def drive(self, throttle_value, steering_value):
        left_speed, right_speed = self.calculate_speeds_car(throttle_value, steering_value)
        self.left_side.drive(left_speed)
        self.right_side.drive(right_speed)
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
    def stop(self):
        self.left_side.stop()
        self.right_side.stop()
    def convert_millimetres_to_milliseconds(self, millimetres, speed):
        milliseconds = int (float(millimetres * self.millimetre_factor) / math.pow(speed, self.speed_exponent))
        return milliseconds
    def convert_degrees_to_milliseconds(self, millimetres, speed):
        degrees = int (float(millimetres * self.degree_factor) / math.pow(speed, self.speed_exponent))
        return degrees

class DriveTrainWithHeadlights(DriveTrain):
    def __init__(self, name, left_side, right_side, left_headlight, right_headlight):
        super().__init__(name, left_side, right_side)
        self.left_headlight = left_headlight
        self.right_headlight = right_headlight
    def fwd(self, speed=50, millimetres=50):
        self.left_headlight.on()
        self.right_headlight.on()
        super().fwd(speed, millimetres)
    def rev(self, speed=50, millimetres=50):
        self.left_headlight.red()
        self.right_headlight.red()
        super().rev(speed, millimetres)
    def spl(self, speed=90, degrees=90):
        self.left_headlight.purple()
        self.right_headlight.off()
        super().spl(speed, degrees)
    def spr(self, speed=90, degrees=90):
        self.left_headlight.off()
        self.right_headlight.purple()
        super().spr(speed, degrees)
    def stop(self):
        self.left_headlight.off()
        self.right_headlight.off()
        super().stop()

class DriveTrainPlus(DriveTrainWithHeadlights):
    def __init__(self, name, left_side, right_side, left_headlight, right_headlight,
                 front_left_ir, front_right_ir, rear_left_ir, rear_right_ir):
        super().__init__(name, left_side, right_side, left_headlight, right_headlight)
        self.front_left_ir = front_left_ir
        self.front_right_ir = front_right_ir
        self.rear_left_ir = rear_left_ir
        self.rear_right_ir = rear_right_ir
    def drive_for(self, throttle_value, steering_value, milliseconds):
        self.drive(throttle_value, steering_value)
        utime.sleep_ms(milliseconds)
        self.stop()
    def drive_while(self, throttle_value, steering_value, obj_list):
        self.drive(throttle_value, steering_value)
        loop_count = 0
        loop_duration = 5
        all_ok = True
        while all_ok:
            for i in range(len(obj_list)):
                obj = obj_list[i][0]
                state = obj_list[i][1]
                current = obj.get()
                if current != state:
                    all_ok = False
            utime.sleep_ms(loop_duration)
            loop_count += 1
            current = obj.get()
        self.stop()
        return loop_count * loop_duration

if __name__ == "__main__":
    print (module_name)
   
    