#  Side.py

import GPIOPico_v12 as GPIOPico
from machine import Pin, PWM, ADC

class Side():

    def __init__(self, name, orientation, motor_list):
        self.name = name
        self.orientation = orientation
        if orientation not in ['L','R']:
            print ("Must be 'L' for left side or 'R' for right side")
            return None
        self.motor_list = motor_list

    def drive(self, speed):  #  speed is from -100 to +100
        if speed > 0:
            self.fwd(speed)
        elif speed < 0:
            self.rev(-speed)
        else:
            self.stop()

    def fwd(self, speed):  #  speed is from 0 to 100
        for motor in self.motor_list:
            if self.orientation == 'L':
                motor.anti(speed)
            else:
                motor.clk(speed)

    def rev(self, speed):  #  speed is from 0 to 100
        for motor in self.motor_list:
            if self.orientation == 'L':
                motor.clk(speed)
            else:
                motor.anti(speed)
    
    def stop(self):
        for motor in self.motor_list:
            motor.stop()
        
    def close(self):
        for motor in self.motor_list:
            motor.close()

if __name__ == "__main__":
    print ('Side_v01.py')
