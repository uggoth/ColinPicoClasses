module_name = 'test_18_F_remote_drive_v01.py'

import PicoE_v08 as PicoE
utime = PicoE.utime
GPIOPico = PicoE.GPIOPico
ColObjects = GPIOPico.ColObjects

throttle = PicoE.ThisRightUpDown()
steering = PicoE.ThisRightSideways()
my_drive_train = PicoE.ThisDriveTrain()
utime.sleep_ms(9)

print ('After Allocate')
print (ColObjects.ColObj.str_allocated())

for i in range(100):
    utime.sleep_ms(100)
    speed = throttle.get()
    print (speed)
    my_drive_train.drive(speed,0)

my_drive_train.stop()

utime.sleep_ms(9)
my_drive_train.close()
throttle.close()
steering.close()

print ('After Close')
print (ColObjects.ColObj.str_allocated())
