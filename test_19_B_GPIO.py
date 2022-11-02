module_name = 'test_19_B_GPIO.py'

import GPIOPico_v17 as GPIOPico
ColObjects = GPIOPico.ColObjects

print (module_name)
print ('------ Allocated GPIOs ---------')
print (GPIOPico.GPIO.str_allocated())
#dummy1 = GPIOPico.LED('expected to fail',55)
dummy2 = GPIOPico.GPIOServo('test servo 2', 2)
#dummy4 = GPIOPico.GPIOServo('test servo 4', 2)
#dummy3 = GPIOPico.LED('expected to fail', 52)
print (GPIOPico.GPIO.str_allocated())
dummy2.close()
print (GPIOPico.GPIO.str_allocated())
