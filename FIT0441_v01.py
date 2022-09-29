#  Utility Objects for motor control

from machine import Pin, PWM
import utime
import math

class FIT0441():
    
    def __init__(self, direction_pin, speed_pin, pulse_pin):
        self.direction_pin = direction_pin
        self.speed_pin = speed_pin
        self.pulse_pin = pulse_pin
        self.pulse_pin.irq(self.pulse_detected)
        self.pulse_count = 0
        self.pulse_checkpoint = 0
        self.duty = 0
        self.stop_duty = 65534
        self.min_speed_duty = 59000
        self.max_speed_duty = 0
        self.clockwise = 1
        self.anticlockwise = 0
        self.name = 'Unknown'

    def set_pulse_checkpoint(self):
        self.pulse_checkpoint = self.get_pulses()

    def get_pulse_checkpoint(self):
        return self.pulse_checkpoint

    def get_pulse_diff(self):
        return self.get_pulses() - self.pulse_checkpoint

    def deinit(self):
        self.speed_pin.deinit()

    def stop(self):
        duty = self.stop_duty
        self.speed_pin.duty_u16(duty)

    def pulse_detected(self, sender):
        self.pulse_count += 1

    def get_pulses(self):
        return self.pulse_count

    def set_speed(self, speed):  #  as a percentage
        self.duty = (self.min_speed_duty
                     - int(float(self.min_speed_duty - self.max_speed_duty)
                        * (float(speed) / 100.0)))
        self.speed_pin.duty_u16(self.duty)
    
    def set_direction(self, direction):  # 1 = clockwise, 0 = anticlockwise
        if direction == 1:
            self.direction_pin.value(self.clockwise)
        elif direction == 0:
            self.direction_pin.value(self.anticlockwise)

class Side():
    
    def __init__(self, motor_list, name='Unknown'):
        self.motor_list = motor_list
        self.speed = 0
        self.direction = 0
        self.name = name
    
    def set_pulse_checkpoints(self):
        for motor in self.motor_list:
            motor.set_pulse_checkpoint()

    def get_pulse_checkpoints(self):
        pulses = {}
        for motor in self.motor_list:
            pulses[motor.name] = motor.get_pulse_checkpoint()
        return pulses        

    def get_pulse_diffs(self):
        diffs = {}
        for motor in self.motor_list:
            diffs[motor.name] = motor.get_pulse_diff()
        return diffs      

    def stop(self):
        for motor in self.motor_list:
            motor.stop()
        self.speed = 0

    def set_speed(self, speed):
        self.speed = speed
        #print (self.name, self.speed)
        for motor in self.motor_list:
            if self.speed < 0:
                motor.set_direction(1)
                motor.set_speed(- self.speed)
            else:
                motor.set_direction(0)
                motor.set_speed(self.speed)


class DriveTrain():
    
    def __init__(self, left_motor_list, right_motor_list):
        self.left_motor_list = left_motor_list
        self.right_motor_list = right_motor_list
        self.left_side = Side(left_motor_list, 'Left Side')
        self.right_side = Side(right_motor_list, 'Right Side')
        self.angle = 0
        self.speed = 0
        self.smoothness = 0
        self.max_increments = 40
        self.pulse_factor = 0.6

    def set_pulse_checkpoints(self):
        left_side.set_pulse_checkpoint()
        right_side.set_pulse_checkpoint()

    def get_pulse_checkpoints(self):
        pulses = {}
        left_pulses = self.left_side.get_pulse_checkpoints()
        for motor_name in left_pulses:
            pulses[motor_name] = left_pulses[motor_name]
        right_pulses = self.right_side.get_pulse_checkpoints()
        for motor_name in right_pulses:
            pulses[motor_name] = right_pulses[motor_name]
        return pulses        

    def get_pulse_diffs(self):
        diffs = {}
        left_diffs = self.left_side.get_pulse_diffs()
        for motor_name in left_diffs:
            diffs[motor_name] = left_diffs[motor_name]
        right_diffs = self.right_side.get_pulse_diffs()
        for motor_name in right_diffs:
            diffs[motor_name] = right_diffs[motor_name]
        return diffs        

    def get_pulses(self):
        diffs = self.get_pulse_diffs()
        total = 0
        for motor in diffs:
            total += diffs[motor]
        avg = int(total / len(diffs))
        return avg

    def get_distance(self):
        return self.pulses_to_millimetres(self.get_pulses())

    def drive(self, angle, speed, smoothness=0, cruise=0):
        # angle: clockwise angle from 0 (straight ahead)
        # speed: percentage of full speed
        # smoothness: milliseconds to accelerate to speed
        # cruise: milliseconds to keep going at speed, or 0 for indefinite
            
        self.angle = int(angle % 360)
        self.speed = int(speed % 100)
        self.smoothness = int(smoothness)
        self.cruise = int(cruise)
        
        if self.smoothness < self.max_increments:
            increments = int(smoothness)
        else:
            increments = self.max_increments

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
            #print ('**** bad angle *****')
            return False

        start = self.get_pulses()
        
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
            max_loops = 1000
            interval = 2
            hit_limit = False
            end = start + self.millimetres_to_pulses(cruise)
            diff = end - start
            for i in range(max_loops):
                utime.sleep_ms(interval)
                if self.get_pulses() >= end:
                    hit_limit = True
                    #print ('pulse limit {:04} hit after {:04} iterations'.format(diff,i))
                    break
            #if not hit_limit:
                #print ('pulse limit not hit')
            self.stop()
        return True
    
    def pulses_to_millimetres(self, pulses):
        return int(pulses * self.pulse_factor)

    def millimetres_to_pulses(self, millimetres):
        return int(millimetres / self.pulse_factor)

    def stop(self):
        self.left_side.stop()
        self.right_side.stop()

class ThisDriveTrain(DriveTrain):  ###### typical instance ################

    def __init__(self):

        self.lf_speed_pin = PWM(Pin(2))                  # blue
        self.lf_pulse_pin = Pin(3, Pin.IN, Pin.PULL_UP)  # green
        self.lf_direction_pin = Pin(4, Pin.OUT)          # yellow
        self.motor_lf = FIT0441(self.lf_direction_pin, self.lf_speed_pin, self.lf_pulse_pin)
        self.motor_lf.name = 'Left Front'

        self.rf_speed_pin = PWM(Pin(6))
        self.rf_pulse_pin = Pin(7, Pin.IN, Pin.PULL_UP)
        self.rf_direction_pin = Pin(8, Pin.OUT)
        self.motor_rf = FIT0441(self.rf_direction_pin, self.rf_speed_pin, self.rf_pulse_pin)
        self.motor_rf.name = 'Right Front'

        self.lb_speed_pin = PWM(Pin(10))
        self.lb_pulse_pin = Pin(11, Pin.IN, Pin.PULL_UP)
        self.lb_direction_pin = Pin(12, Pin.OUT)
        self.motor_lb = FIT0441(self.lb_direction_pin, self.lb_speed_pin, self.lb_pulse_pin)
        self.motor_lb.name = 'Left Back'

        self.rb_speed_pin = PWM(Pin(21))
        self.rb_pulse_pin = Pin(20, Pin.IN, Pin.PULL_UP)
        self.rb_direction_pin = Pin(19, Pin.OUT)
        self.motor_rb = FIT0441(self.rb_direction_pin, self.rb_speed_pin, self.rb_pulse_pin)
        self.motor_rb.name = 'Right Back'

        self.left_motor_list = [self.motor_lb, self.motor_lf]
        self.right_motor_list = [self.motor_rb, self.motor_rf]
        self.all_motors_list = [self.motor_lb, self.motor_lf, self.motor_rb, self.motor_rf]
        super().__init__(self.left_motor_list, self.right_motor_list)
    
    def close(self):
        self.stop()
        utime.sleep(0.01)
        self.lb_speed_pin.deinit()
        self.rb_speed_pin.deinit()
        self.lf_speed_pin.deinit()
        self.rf_speed_pin.deinit()
        
if __name__ == "__main__":
    print ('FIT0441_v01.py')
