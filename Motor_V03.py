module_name = 'Motor_V03.py'
module_description = 'General definition of all motors. Created 11/Jul/2023'

if __name__ == "__main__":
    print (module_name, 'starting')

import ColObjects_V14 as ColObjects
import GPIOPico_V29 as GPIO
import utime
import machine

class FIT0441Motor(ColObjects.Motor):
    def __init__(self, name, direction_pin_no, speed_pin_no, pulse_pin_no):
        super().__init__(name)
        self.direction_pin_GPIO = GPIO.GPIO(pin_no=direction_pin_no, type_code='MOTOR', name=name+'_direction_'+str(direction_pin_no))
        self.direction_pin = machine.Pin(direction_pin_no, machine.Pin.OUT)
        self.speed_pin_GPIO = GPIO.GPIO(pin_no=speed_pin_no, type_code='MOTOR', name=name+'_speed_'+str(speed_pin_no))
        self.speed_pin = machine.PWM(machine.Pin(speed_pin_no))
        self.pulse_pin_GPIO = GPIO.GPIO(pin_no=pulse_pin_no, type_code='MOTOR', name=name+'_pulse_'+str(pulse_pin_no))
        self.pulse_pin = machine.Pin(pulse_pin_no, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pulse_pin.irq(self.pulse_detected, machine.Pin.IRQ_FALLING)
        self.pulse_count = 0
        self.pulse_checkpoint = 0
        self.pulse_endpoint = 0
        self.duty = 0
        self.stop_duty = 65534
        self.min_speed_duty = 65000
        self.max_speed_duty = 0
        self.clockwise = 1
        self.anticlockwise = 0

    def __str__(self):
        outstring = self.name
        outstring += ', speed pin: ' + str(self.speed_pin_GPIO.pin_no)
        outstring += ', direction pin: ' + str(self.direction_pin_GPIO.pin_no)
        outstring += ', pulse pin: ' + str(self.pulse_pin_GPIO.pin_no)
        return outstring

    def clk(self, speed):
        self.direction_pin.value(self.clockwise)
        self.set_speed(speed)

    def anti(self, speed):
        self.direction_pin.value(self.anticlockwise)
        self.set_speed(speed)

    def pulse_detected(self, sender):
        self.pulse_count += 1
        if self.pulse_endpoint > 0:
            if self.pulse_count >= self.pulse_endpoint:
                self.stop()

    def get_pulses(self):
        return self.pulse_count

    def deinit(self):
        self.pulse_pin.irq(None)
        self.speed_pin.deinit()

    def stop(self):
        duty = self.stop_duty
        self.speed_pin.duty_u16(duty)
        utime.sleep_ms(1)
        
    def close(self):
        self.deinit()
        utime.sleep_ms(5)
        self.direction_pin_GPIO.close()
        self.speed_pin_GPIO.close()
        self.pulse_pin_GPIO.close()
        super().close()

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

class L298NMotor(ColObjects.Motor):
    def __init__(self, name, clk_pin_no, anti_pin_no):
        super().__init__(name)
        #  clk is clockwise looking at the motor from the wheel side
        self.stop_duty = 0
        self.max_speed = 100  #  as an integer percentage
        self.min_speed = 0
        self.min_speed_duty = 0
        self.max_speed_duty = 65534
        self.speed = self.min_speed
        self.freq = 25000
        self.clk_pin_GPIO = GPIO.GPIO(pin_no=clk_pin_no, type_code='MOTOR', name=name+'_clk_'+str(clk_pin_no))
        self.clk_pin = machine.Pin(clk_pin_no)
        self.clk_PWM = machine.PWM(self.clk_pin)
        self.clk_PWM.freq(self.freq)
        self.clk_PWM.duty_u16(self.stop_duty)
        self.anti_pin_GPIO = GPIO.GPIO(pin_no=anti_pin_no, type_code='MOTOR', name=name+'_anti_'+str(anti_pin_no))
        self.anti_pin = machine.Pin(anti_pin_no)
        self.anti_PWM = machine.PWM(self.anti_pin)
        self.anti_PWM.freq(self.freq)
        self.anti_PWM.duty_u16(self.stop_duty)
    def __str__(self):
        outstring = self.name
        outstring += ', clockwise pin: ' + str(self.clk_pin_GPIO.pin_no)
        outstring += ', anticlockwise pin: ' + str(self.anti_pin_GPIO.pin_no)
        return outstring
    def convert_speed_to_duty(self, speed):
        duty = int((self.max_speed_duty - self.min_speed_duty) / 100 * speed)
        return duty
    def clk(self, speed):
        self.anti_PWM.duty_u16(self.stop_duty)
        self.clk_PWM.duty_u16(self.convert_speed_to_duty(speed))
    def anti(self, speed):
        self.clk_PWM.duty_u16(self.stop_duty)
        self.anti_PWM.duty_u16(self.convert_speed_to_duty(speed))
    def stop(self):
        self.clk_PWM.duty_u16(self.stop_duty)
        self.anti_PWM.duty_u16(self.stop_duty)
    def close(self):
        self.clk_PWM.deinit()
        self.anti_PWM.deinit()
        utime.sleep_ms(5)
        self.clk_pin_GPIO.close()
        self.anti_pin_GPIO.close()
        super().close()

class Side(ColObjects.ColObj):
    def __init__(self, name, which_side, my_motors):
        super().__init__(name)
        self.which_side = which_side
        self.my_motors = my_motors
    def __str__(self):
        outstring = ''
        outstring += self.name + '\n'
        i = 0
        for motor in self.my_motors:
            outstring += self.name + ' motor' + str(i) + ': ' + str(motor) + '\n'
            i += 1
        return outstring
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

if __name__ == "__main__":
    name = 'Test FIT0441'
    speed_pin_no = 6
    direction_pin_no = 7
    pulse_pin_no = 8
    test_motor_1 = FIT0441Motor(name, direction_pin_no, speed_pin_no, pulse_pin_no)

    name = 'Test L298N'
    clk_pin_no = 16
    anti_pin_no = 17
    test_motor_2 = L298NMotor(name, clk_pin_no, anti_pin_no)

    name = 'Test Side'
    which_side = 'L'
    my_motors = [test_motor_1, test_motor_2]
    test_side = Side(name, which_side, my_motors)
    
    print ('--- INSTANTIATED --')
    print (ColObjects.ColObj.str_allocated())
    test_side.close()
    test_motor_1.close()
    test_motor_2.close()
    print ('--- AFTER CLOSE --')
    print (ColObjects.ColObj.str_allocated())
    print (module_name, 'finished')
