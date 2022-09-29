#  Utility Objects for motor control (no local line following)

from machine import Pin, PWM
import utime

class Button():
    
    def __init__(self, pin_no, rgb_led):
        self.pin_no = pin_no
        self.signal = Pin(pin_no, Pin.IN)  #  , Pin.PULL_UP)  #  if no built in
        self.rgb_led = rgb_led
        self.waiting = False

    def button_pressed(self, event):
        self.signal.irq(handler=None)
        self.rgb_led.blue.off()
        self.waiting = False

    def leds_off(self):
        self.rgb_led.off()

    def wait(self, seconds):
        self.signal.irq(trigger=Pin.IRQ_FALLING, handler=self.button_pressed)
        self.rgb_led.blue.on()
        self.waiting = True
        milliseconds = seconds * 1000
        pause = 5
        loops = milliseconds / pause
        for i in range(loops):
            if not self.waiting:
                break
            utime.sleep_ms(pause)
        self.signal.irq(handler=None)
        self.rgb_led.blue.off()
        return not self.waiting

if __name__ == "__main__":
    print ('Button_v01.py')
