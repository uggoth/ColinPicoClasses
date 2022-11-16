import PicoP_v01 as Pico
GPIOPico = Pico.GPIOPico
import utime

module_name = 'test_01_D_switches_v01.py'
print (module_name, 'starting')

these_switches = Pico.TheseSwitches()

my_switches = GPIOPico.Switch.switch_list

for switch in my_switches:
    switch.previous = 'UNKNOWN'

print (my_switches)

for i in range(100):
    utime.sleep(0.1)
    for switch in my_switches:
        current = switch.get()
        if current != switch.previous:
            print (switch.name, current)
            switch.previous = current

print (module_name, 'finished')
