import utime
import machine

module_name = 'test_01_A_digital_inputs_raw_v02.py'

print (module_name, "starting")
print ("")

gpio_list = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,26,27,28]

gpios = []
for gpio in gpio_list:
    gpios.append(machine.Pin(gpio, machine.Pin.IN, machine.Pin.PULL_UP))

output = ''
for i in range(len(gpio_list)):
    output += "{0:02d} ".format(gpio_list[i])
print (output)

for i in range(10):
    output = ' '
    for j in range(len(gpio_list)):
        output += str(gpios[j].value()) + "  "
    print (output)
    utime.sleep_ms(1000)

print ("")
print (module_name, "finished")
