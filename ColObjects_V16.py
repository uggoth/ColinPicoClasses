module_name = 'ColObjects_V16.py'
module_decription = 'Foundation abstract objects. Created 11/Aug/2023'

if __name__ == "__main__":
    print (module_name, 'starting')

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
    
    def __init__(self, name, description=''):
        self.name = name
        if name in ColObj.allocated:
            if ColObj.allocated[self.name] != ColObj.free_code:
                raise ColError(name + ' already allocated')
        ColObj.allocated[self.name] = self
        self.description = description
        
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

class Joystick(ColObj):
    def __init__(self, name, receiver, channel, interpolator):
        self.name = name
        self.receiver = receiver
        self.channel = channel
        self.interpolator = interpolator
    def get(self):
        channel_values = self.receiver.get()
        this_value = self.interpolator.interpolate(channel_values[self.channel])
        return this_value

class Servo(ColObj):
    def __init__(self, name, description=''):
        super().__init__(name, description)
    def move_to(self, angle):
        raise ColError('**** Must be overriden')

class Motor(ColObj):
    def __init__(self, name, description=''):
        super().__init__(name, description)
    def clk(self, speed):
        raise ColError('**** Must be overriden')
    def anti(self, speed):
        raise ColError('**** Must be overriden')
    def stop(self):
        raise ColError('**** Must be overriden')


class PIO(ColObj):
    
    allocated = {}
    free_code = '--FREE--'
    pio_no = 0
    for i in range(2):  #  There are two blocks. Block 0 is conventionally used for remote control
                        #                        Block 1 is conventionally used for neopixels
                        #  This avoids running out of code space as code gets re-used
                        #  On the Pico W, state machine 4 is used for wireless
        allocated[i] = {}
        for j in range(4):   #  each block has 4 PIOs
            allocated[i][j] = {'PIO':pio_no,'NAME':free_code}
            pio_no += 1
    allocated[1][0]['NAME'] = 'WIRELESS'
    
    def str_allocated():
        out_string = ('{:3}'.format('PIO') +
                      '  {:18}'.format('NAME') + '\n')
        for i in range(2):
            for j in range(4):
                out_string += ('{:3}'.format(PIO.allocated[i][j]['PIO'])  +
                               '  {:18}'.format(PIO.allocated[i][j]['NAME']) + '\n')
        return out_string

    def allocate(name, block):
        for j in range(4):
            if PIO.allocated[block][j]['NAME'] == PIO.free_code:
                PIO.allocated[block][j]['NAME'] = name
                return PIO.allocated[block][j]['PIO']
        return None        
        
    def deallocate(pio_no):
        for i in range(2):
            for j in range(4):
                if PIO.allocated[i][j]['PIO'] == pio_no:
                    PIO.allocated[i][j]['NAME'] = PIO.free_code
                    return True
        return False

    def __init__(self, name, block_no):
        super().__init__(name)
        self.block_no = block_no
        self.pio_no = PIO.allocate(name, block_no)
        if self.pio_no is None:
            print (PIO.str_allocated())
            raise ColError('**** Could not get PIO')

    def __str__(self):
        out_string = 'PIO: ' + self.name
        out_string += ', state_machine_no: ' + str(self.pio_no)
        out_string += ', block: ' + str(self.block_no)
        return out_string

    def close(self):
        PIO.deallocate(self.pio_no)
        super().close()

class RGBLED(ColObj):
    def __init__(self, name, red_led, green_led, blue_led):
        response = super().__init__(name)
        self.red_led = red_led
        self.green_led = green_led
        self.blue_led = blue_led
        
    def on(self):
        self.red_led.on()
        self.green_led.on()
        self.blue_led.on()

    def red(self):
        self.red_led.on()
        self.green_led.off()
        self.blue_led.off()

    def green(self):
        self.red_led.off()
        self.green_led.on()
        self.red_led.off()

    def blue(self):
        self.red_led.off()
        self.green_led.off()
        self.blue_led.on()

    def purple(self):
        self.red_led.on()
        self.green_led.off()
        self.blue_led.on()

    def orange(self):
        self.red_led.on()
        self.green_led.on()
        self.blue_led.off()

    def off(self):
        self.red_led.off()
        self.green_led.off()
        self.blue_led.off()
        
    def close(self):
        self.off()
        self.red_led.close()
        self.green_led.close()
        self.blue_led.close()
        

if __name__ == "__main__":
    print (module_name,'testing instantiation')
    d1 = PIO('Fred',1)
    d2 = PIO('Bill',1)
    d3 = PIO('George',0)
    print (PIO.str_allocated())
    print (d1)
    print (d2)
    print (d3)
    PIO.deallocate(4)
    print (PIO.str_allocated())
    print (module_name, 'finished')