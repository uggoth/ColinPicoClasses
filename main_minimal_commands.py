# serial testing main_col_echo_v01.py
import machine
import utime
import GPIO_v02 as GPIO
import CommandStream_v01 as CommandStream

my_stream = CommandStream.CommandStream()

if not my_stream.valid:
    print ('**** Failed to open stream')

led_onboard=GPIO.LED(25,'onboard')

while True:
    message = my_stream.get(1)
    if not message:
        continue
    else:
        command = message[0:4]
        if command == 'WHOU':
            my_stream.send (colobj.who_me)
        elif command == 'SOFT':
            my_stream.send ('main_col_led_v09.py')
        elif command == 'BLON':
            my_stream.send('OKOK')
            led_onboard.on()
        elif command == 'BLOF':
            my_stream.send('OKOK')
            led_onboard.off()
        elif command == 'ECHO':
            my_stream.send ('ECHO:' + command)
        elif command == 'EXIT':
            my_stream.send ('Exiting')
            break
        else:
            my_stream.send (command)

my_stream.close()
