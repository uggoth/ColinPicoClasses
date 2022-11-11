module_name = 'main_radio_tank_car_v10.py'

import PicoA_v15 as PicoA
GPIOPico = PicoA.GPIOPico
import utime
from machine import Pin

def do_lights():
    global old_pos
    pos = my_knob.get()
    if pos != old_pos:
        old_pos = pos
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

old_pos = 999

my_headlight = PicoA.ThisRunningLights()
my_knob = PicoA.ThisKnob()

my_headlight.clear()

print (module_name,'starting')
my_remote_control = PicoA.ThisRemoteControl()

utime.sleep_ms(200)

lights_interval = 10

i = 0
while True:  #  arbitrary test duration
    i += 1
    utime.sleep_ms(1)
    my_remote_control.drive()
    if i % lights_interval == 0:
        do_lights()

print ('stopping')
my_knob.close()
my_remote_control.close()

