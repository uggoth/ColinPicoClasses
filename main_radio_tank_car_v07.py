#  main_radio_tank_v07.py

import PicoA_v04 as PicoA
import utime
from machine import Pin
import neopixel

def show_ring(pixels, start, mode):
    if mode == 'OFF':
        pixels.clear()
        pixels.show()
        return
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    white = (255,255,255)
    off = (0,0,0)
    pixels[0] = white
    pattern = [off,red,off,green,off,blue]
    #print ((start+0)%7,(start+5)%6)
    pixels[1] = pattern[(start+0)%6]
    pixels[2] = pattern[(start+1)%6]
    pixels[3] = pattern[(start+2)%6]
    pixels[4] = pattern[(start+3)%6]
    pixels[5] = pattern[(start+4)%6]
    pixels[6] = pattern[(start+5)%6]
    pixels.show()

obled = Pin(20,Pin.OUT)

for i in range(10):
    obled.on()
    utime.sleep(0.2)
    obled.off()
    utime.sleep(0.1)

no_pixels = 7
state_machine = 0
pin=27
mode = 'GRB'
pixels = neopixel.Neopixel(no_pixels, state_machine, pin, mode)
knob = PicoA.ThisKnob()

my_remote_control = PicoA.ThisRemoteControl()
utime.sleep_ms(200)
my_rgb = PicoA.ThisRGBLED()

print ('starting')

interval = 10
i = 0
while True:  #  arbitrary test duration
    utime.sleep_ms(1)
    mode = my_remote_control.mode
    i += 1
    if (i % interval) == 0:
        diff = int(knob.get())
        show_ring(pixels, diff, mode)
    if mode == 'TANK':
        my_rgb.blue()
    elif mode == 'CAR':
        my_rgb.green()
    else:
        my_rgb.off()
    left_speed, right_speed = my_remote_control.drive()

print ('stopping')
my_remote_control.stop()
my_remote_control.close()
my_rgb.off()