module_name = 'test_18_D_remote_control_v01.py'

import PicoA_v08 as PicoA
import utime

print (module_name)

my_remote_control = PicoA.ThisRemoteControl()

for i in range(20):
    utime.sleep_ms(500)
    print (my_remote_control.calculate_speeds())

my_remote_control.close()
