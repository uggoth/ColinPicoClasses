module_name = 'main_neopixel_C_v01.py'

import PicoP_v01 as Pico
import utime

print (module_name,'starting')

my_strip = Pico.ThisStrip()
my_buttons = Pico.TheseButtons()
my_green_button = my_buttons.green_button #  indicate right
my_red_button = my_buttons.red_button  #  indicate left
my_switches = Pico.TheseSwitches()
my_dip_1 = my_switches.dip_1  #  on / off
my_dip_2 = my_switches.dip_2  #  flash / steady
my_dip_3 = my_switches.dip_3  #  blue / no blue

display = {}
display['normal'] = {'back_left':'red', 'left':'off', 'front':'white', 'right':'off', 'back_right':'red'}
display['left'] = {'back_left':'red', 'left':'orange', 'front':'white', 'right':'off', 'back_right':'red'}
display['right'] = {'back_left':'red', 'left':'off', 'front':'white', 'right':'orange', 'back_right':'red'}
display['blue'] = {'back_left':'off', 'left':'blue', 'front':'off', 'right':'blue', 'back_right':'off',
                    'bl_interval':'blue','lf_interval':'blue','fr_interval':'blue','rb_interval':'blue'}
display['off'] = {'all':'off'}

def do_display(which_display):
    part = display[which_display]
    for sector in part:
        my_strip.fill_sector(sector, part[sector])
    my_strip.show()

utime.sleep_ms(10)
my_strip.fill_sector('warning','green')
my_strip.show()
utime.sleep_ms(3)

flip_flop = True
display_code = 'off'
while True:
    do_display(display_code)
    dip_1_state = my_dip_1.get()  #  on / off
    dip_2_state = my_dip_2.get()  #  flash / steady
    dip_3_state = my_dip_3.get()  #  blue / no blue
    utime.sleep_ms(off_time)
    if dip_1_state != 'ON':
        display_code = 'off'   #  display off
        continue
    flip_flop = not flip_flop
    if flip_flop:  #  not flash period
        if dip_2_state != 'ON':   #  steady
            display_code = 'normal'
            continue
        else:
            display_code = 'off'
    else:  #  flash period
        if my_red_button.get() == 'ON':
            display_code = 'left'
            continue
        if my_green_button.get() == 'ON':
            display_code = 'right'
            continue
        if dip_3_state == 'ON':
            display_code = 'blue'
        else:
            display_code = 'off'

    

my_strip.close()

print (module_name,'finished')
