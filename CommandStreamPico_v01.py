#  Utility Objects for communication with controlling Raspberry Pi

from machine import Pin, PWM
import utime
import sys, select

class CommandStream():
    
    in_use = False
    
    def __init__(self):
        if CommandStream.in_use:
            self.valid = False
        else:
            CommandStream.in_use = True
            self.valid = True
    
    def close(self):
        CommandStream.in_use = False

    def get(self, delay=0.001):
        inputs, outputs, errors = select.select([sys.stdin],[],[],delay)
        if (len(inputs) > 0):
            result = sys.stdin.readline()
        else:
            result = False
        return result
 
    def send(self, message):
        print (message)
 
    def flush(self):
        no_inputs = 1
        while no_inputs > 0:
            inputs, outputs, errors = select.select([sys.stdin],[],[],0.001)
            if (len(inputs) > 0):
                result = sys.stdin.readline()
            else:
                break

if __name__ == "__main__":
    print ('CommandStream_v01.py')
