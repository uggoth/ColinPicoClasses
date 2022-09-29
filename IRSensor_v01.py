#  Utility Objects for motor control (no local line following)

from machine import Pin, PWM
import utime
        
class IRSensor():
    def __init__(self, pin, pin_level, irq_callback):
        self.name = 'Unknown'
        self.pin = pin
        self.pin_level = pin_level
        self.irq_callback = irq_callback
        #  callback parms will be: pin, pin_level, value
        #  -- EXAMPLE --
        #  def my_callback(pin, pin_level, value):
        #      print (pin, pin_level, value)
        #      return True   #  if want IRQ left off
        self.pin.irq(trigger=pin_level, handler=self.event_occured)

    def event_occured(self, device):
        device.irq(handler=None)
        utime.sleep_us(10)   # slight debounce ##########################
        value_1 = device.value()
        utime.sleep_us(50)
        value_2 = device.value()
        if value_1 == value_2:
            if self.irq_callback(value_2):
                return
        device.irq(trigger=self.pin_level, handler=self.event_occured)
    
    def close(self):
        self.pin.irq(handler=None)

class LeftIRArriving(IRSensor):
    def __init__(self, irq_callback):
        super().__init__(Pin(18, Pin.IN, Pin.PULL_UP), Pin.IRQ_FALLING, irq_callback)
        self.name = "Left IR Arriving"
        
class RightIRArriving(IRSensor):
    def __init__(self, irq_callback):
        super().__init__(Pin(22, Pin.IN, Pin.PULL_UP), Pin.IRQ_FALLING, irq_callback)
        self.name = "Right IR Arriving"
        
if __name__ == "__main__":
    print ('IRSensor_v01.py')
