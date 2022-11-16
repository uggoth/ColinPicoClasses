import PicoP_v01 as Pico
GPIOPico = Pico.GPIOPico
import utime

module_name = 'test_01_C_buttons_v01.py'
print (module_name, 'starting')

these_buttons = Pico.TheseButtons()

my_buttons = GPIOPico.Button.button_list

for button in my_buttons:
    button.previous = 'UNKNOWN'

print (my_buttons)

for i in range(100):
    utime.sleep(0.1)
    for button in my_buttons:
        current = button.get()
        if current != button.previous:
            print (button.name, current)
            button.previous = current

print (module_name, 'finished')
