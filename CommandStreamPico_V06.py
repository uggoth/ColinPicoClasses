module_name = 'CommandStreamPico_V06.py'
last_updated = '30/Jan/2024'

#  Utility Object for communication with controlling Raspberry Pi

import sys, select
import ColObjects_V16 as ColObjects

class CommandStream(ColObjects.ColObj):
    
    in_use = False
    
    def __init__(self, name, handshake_object):
        super().__init__(name, 'Command Stream from Pi')
        if CommandStream.in_use:
            self.valid = False
        else:
            CommandStream.in_use = True
            self.valid = True
        self.handshake_object = handshake_object
        
    def ready(self):
        if self.handshake_object is not None:
            self.handshake_object.set('OFF')

    def not_ready(self):
        if self.handshake_object is not None:
            self.handshake_object.set('ON')

    def close(self):
        self.not_ready()
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
    print (module_name)
