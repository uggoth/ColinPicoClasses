module_name = 'main_K_football_v06.py'

import ThisPico_F_v18 as ThisPico
import utime
import sys

print (module_name, 'starting')

def close_down():
    ThisPico.ThisPico.close_all()
    logfile.write('VSYS: {:}'.format(my_vsys.read())+'\n')
    logfile.write('Closing down')
    logfile.close()

my_board = ThisPico.Kitronik.Kitronik('The Only Board')
my_left_headlight = ThisPico.ThisLeftHeadlight()
my_right_headlight = ThisPico.ThisRightHeadlight()
my_drive_train = ThisPico.ThisDriveTrainWithHeadlights(my_board, my_left_headlight, my_right_headlight)
my_remote_control = ThisPico.ThisRemoteControlWithHeadlights(my_drive_train)
my_kick_switch = my_remote_control.kick_switch
my_shoulder_servo = ThisPico.ThisShoulderServo(my_board)
my_buttons = ThisPico.TheseButtons()
yellow_button = my_buttons.yellow_button
my_irs = ThisPico.TheseIRSensors()
my_led = ThisPico.ThisStrip()
my_switches = ThisPico.TheseSwitches()
my_us = ThisPico.ThisHCSR04()
my_buzzer = ThisPico.ThisBuzzer()
my_vsys = ThisPico.onboard_volts

def check_for_recoil():
    for ir in my_irs.ir_list:
        if ir.get() != 'ON':
            if ir.name[0:4] == 'FRON':
                print ('Reversing')
                my_buzzer.play_tone(244)
                my_drive_train.rev(speed=50, millimetres=70)
                my_buzzer.be_quiet()
                if ir.name[6:10] == 'LEFT':
                    my_drive_train.spr(90,20)
                else:
                    my_drive_train.spl(90,20)
            else:
                print ('Avoiding')
                my_buzzer.play_tone(244)
                my_drive_train.fwd(speed=50, millimetres=70)
                my_buzzer.be_quiet()
                if ir.name[5:9] == 'LEFT':
                    my_drive_train.spl(90,20)
                else:
                    my_drive_train.spr(90,20)

def kick_switch_on():
    new_position = my_kick_switch.get()
    if new_position > 85:
        return False
    else:
        return True

def volts_low(v):
    if v > my_vsys.good_volts:
        my_led.set_pixel(1,my_led.colours['blue'])
        return False
    elif v > my_vsys.bad_volts:
        my_led.set_pixel(1,my_led.colours['green'])
        return False
    else:
        print (v)
        my_led.set_pixel(1,my_led.colours['red'])
        return True
            
def do_remote():
    previous_pose = 'UNKNOWN'
    old_position = 999
    direction = 1  #  down
    margin = 5
    interval = 1000
    count = 0
    while True:
        count += 1
        utime.sleep_ms(2)
        v = my_vsys.read()
        if count % interval == 0:
            logfile.write('VSYS: {:}'.format(v))
        if volts_low(v):
            break
        if kick_switch_on():
            my_shoulder_servo.move_to(180)
        else:
            my_shoulder_servo.move_to(110)
        if yellow_button.get() == 'ON':
            my_led.set_pixel(0,my_led.colours['yellow'])
            break
        my_remote_control.drive()
        check_for_recoil()

def logit(name, value):
    out = '{:} = {:}'.format(name, value)
    print (out)
    logfile.write(out+'\n')

logfile = open('logfile.txt', 'w')

print ('--- waiting ----')
flip_flop = True
while True:
    if flip_flop:
        my_led.on()
    else:
        my_led.off()
    flip_flop = not flip_flop
    utime.sleep_ms(100)
    if kick_switch_on():
        break

print ('--- starting ---')
my_led.off()
my_led.set_pixel(0,my_led.colours['green'])
previous_pose = 'UNKNOWN'
servo_speed = 50

do_remote()

my_led.set_pixel(2,my_led.colours['red'])
utime.sleep(4)
close_down()
print (module_name, 'finished')
