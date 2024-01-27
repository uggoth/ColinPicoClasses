module_name = 'CommandStreamPico_V04.py'

#  Utility Object for communication with controlling Raspberry Pi

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
        self.valid = False

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
    print (module_name, 'starting')
    import utime
    print ('Before. in use?', CommandStream.in_use)
    tempcs = CommandStream()
    print ('After. in use?', CommandStream.in_use)
    print ('After. valid?', tempcs.valid)
    tempcs.send('testingg')
    utime.sleep(1)
    failcs = CommandStream()
    print ('Fail. valid?', failcs.valid)
    tempcs.close()
    print ('Closed. in use?', CommandStream.in_use)
    print ('Closed. valid?', tempcs.valid)
    print (module_name, 'finished')
    
