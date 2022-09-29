#  RGB LED

from machine import Pin, PWM
import utime

class RGBLED():
    def __init__(self, red_pin_no, green_pin_no, blue_pin_no):
        self.red = Pin(red_pin_no, Pin.OUT)
        self.green = Pin(green_pin_no, Pin.OUT)
        self.blue = Pin(blue_pin_no, Pin.OUT)
    def off(self):
        self.red.off()
        self.green.off()
        self.blue.off()

if __name__ == "__main__":
    print ('RGB_LED.py for Pico')
