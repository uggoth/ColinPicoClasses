module_name = 'test_03_F_neopixel.py'

import PicoA_v15 as PicoA
import machine
import utime

print (module_name, 'starting')

def do_lights(pos):
    if pos < 1:
        my_headlight.set_mode('off')
    elif pos < 2:
        my_headlight.set_mode('dipped')
    elif pos < 3:
        my_headlight.set_mode('full')
    elif pos < 4:
        my_headlight.set_mode('hazard')
    else:
        my_headlight.set_mode('blues')

my_headlight = PicoA.ThisRunningLights()
my_knob = PicoA.ThisKnob()

my_headlight.clear()
utime.sleep(0.5)

old_pos = 999

for i in range(5000):
    pos = my_knob.get()
    if pos != old_pos:
        print ('new', pos)
        do_lights(pos)
        old_pos = pos
    utime.sleep_ms(5)

my_headlight.close()
my_knob.close()
print (module_name, 'finished')
