import machine
import utime

class GPIO():

    valid_pin_nos = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,26,27,28,29]
    valid_type_codes = {'INFRA_RED':'INPUT',
                        'BUTTON':'INPUT',
                        'US_TRIGGER':'OUTPUT',
                        'US_ECHO':'INPUT',
                        'SWITCH':'INPUT',
                        'VOLTS':'INPUT',
                        'LED':'OUTPUT',
                        'MOTOR':'OUTPUT'}
    allocated = {}
    allocated_by_type = {}
    allocated_str = ''
    for type_code in valid_type_codes:
        allocated_by_type[type_code] = {}
    
    def __init__(self, pin_no, type_code, name):
        self.valid = False
        if pin_no not in GPIO.valid_pin_nos:
            print (pin_no,'not in',GPIO.valid_pin_nos)
            return
        self.pin_no = pin_no
        if type_code not in GPIO.valid_type_codes:
            print (type_code,'not in',GPIO.valid_type_codes)
            return
        self.type_code = type_code
        if self.pin_no in GPIO.allocated:
            print (self.pin_no,'already allocated')
            return
        self.name = name
        self.valid = True
        self.previous = 'UNKNOWN'
        GPIO.allocated[self.pin_no] = self
        GPIO.allocated_by_type[self.type_code][self.pin_no] = self
        GPIO.allocated_str += str(self.pin_no) + ':' + self.name + ':' + str(self) + '\n\r'
        
    def str_allocated(self):
        out_string = ''
        for device in sorted(GPIO.allocated):
            obj = GPIO.allocated[device]
            out_string += ('{:02}'.format(device) + ' : ' +
                            '{:18}'.format(obj.name) + ' : ' +
                            str(obj) + "\n")
        return out_string



class L298NMotor():
    def __init__(self, name, fwd_pin_no, rev_pin_no):
        self.name = name
        self.stop_duty = 0
        self.freq = 25000
        self.fwd_pin_GPIO = GPIO(pin_no=fwd_pin_no, type_code='MOTOR', name=name+'_fwd_'+str(fwd_pin_no))
        self.fwd_pin = machine.Pin(fwd_pin_no)
        self.fwd_PWM = machine.PWM(self.fwd_pin)
        self.fwd_PWM.freq(self.freq)
        self.fwd_PWM.duty_u16(self.stop_duty)
        self.rev_pin_GPIO = GPIO(pin_no=rev_pin_no, type_code='MOTOR', name=name+'_rev_'+str(rev_pin_no))
        self.rev_pin = machine.Pin(rev_pin_no)
        self.rev_PWM = machine.PWM(self.rev_pin)
        self.rev_PWM.freq(self.freq)
        self.rev_PWM.duty_u16(self.stop_duty)
        self.min_speed_duty = 590
        self.max_speed_duty = 65534
    def fwd(self, speed):
        self.rev_PWM.duty_u16(self.stop_duty)
        duty = int(self.max_speed_duty / 100 * speed)
        self.fwd_PWM.duty_u16(duty)
    def rev(self, speed):
        self.fwd_PWM.duty_u16(self.stop_duty)
        duty = int(self.max_speed_duty / 100 * speed)
        self.rev_PWM.duty_u16(duty)
    def deinit(self):
        self.fwd_PWM.deinit()
        self.rev_PWM.deinit()
    def stop(self):
        self.fwd_PWM.duty_u16(self.stop_duty)
        self.rev_PWM.duty_u16(self.stop_duty)



class Sensor(GPIO):
    
    sensor_list = []
    
    def __init__(self, pin_no, type_code, name):
        super().__init__(pin_no, type_code, name)
        if not self.valid:
            return
        self.state = 'UNKNOWN'
        Sensor.sensor_list.append(self)


class Button(Sensor):
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'BUTTON', name)
        if not self.valid:
            return
        self.pin_no = pin_no
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN, machine.Pin.PULL_UP)
        self.latched = False
        
    def get(self):
        if self.pin.value() == 0:
            self.state = 'ON'
            self.latched = True
        elif self.pin.value() == 1:
            self.state = 'OFF'
        else:
            self.state = 'UNKNOWN'
        return self.state
    
    def wait(self, seconds=100, LED=None):
        flash_iterations = 100
        flip_flop = True
        loops = seconds * 1000
        for i in range(loops):   #  wait maximum of 100 seconds
            if LED is not None:
                if i % flash_iterations == 0:
                    if flip_flop:
                        LED.on()
                    else:
                        LED.off()
                    flip_flop = not flip_flop
            response = self.get()
            if self.latched:
                self.latched = False
                if LED is not None:
                    LED.off()
                return True
            utime.sleep_ms(1)
        if LED is not None:
            LED.off()
        return False
        

class Volts(Sensor):
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'VOLTS', name)
        if not self.valid:
            return
        self.pin_no = pin_no
        self.pin = machine.ADC(pin_no)
        self.warning_level = 5.0
        self.volts = 0.0
        self.state = 'UNKNOWN'
    
    def read(self):
        conversion_factor = 0.000164
        raw = self.pin.read_u16()
        self.volts = raw * conversion_factor
        return self.volts
    
    def get(self):
        volts = self.read()
        if volts < self.warning_level:
            self.state = 'OFF'
        else:
            self.state = 'ON'
        return self.state

class USTrigger(Sensor):
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'US_TRIGGER', name)
        self.pin_no = pin_no
        self.pin = machine.Pin(self.pin_no, machine.Pin.OUT)
        self.valid = True

class USEcho(Sensor):    
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'US_ECHO', name)
        self.pin_no = pin_no
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN)
        self.valid = True

class HCSR04():
    def __init__(self,
                 trigger_pin_no,
                 echo_pin_no,
                 name,
                 critical_distance):
        self.type = 'HCSR04'
        self.name = name
        self.trigger_object = USTrigger(trigger_pin_no, name + '_TRIGGER')
        self.trigger = self.trigger_object.pin
        self.echo_object = USEcho(echo_pin_no, name + '_ECHO')
        self.echo = self.echo_object.pin
        self.error_code = 0
        self.error_message = ""
        self.critical_distance = critical_distance
        self.distance = -1
        self.last_distance_measured = -1
        
    def get(self):
        mm = self.millimetres()
        if mm < self.critical_distance:
            self.state = 'ON'
        else:
            self.state = 'OFF'
        return self.state

    def millimetres(self):
        start_ultra = utime.ticks_us()
        self.trigger.low()
        utime.sleep_ms(10)
        self.trigger.high()
        utime.sleep_us(10)
        self.trigger.low()
        success = False
        for i in range(20000):
            if self.echo.value() == 1:
                signaloff = utime.ticks_us()
                success = True
                break
        if not success:
            duration1 = (utime.ticks_us() - start_ultra) / 1000
            self.error_code = 1
            self.error_message = "Failed 1 after " + str(duration1) + " milliseconds"
            return 0
        success = False
        for i in range(10000):
            if self.echo.value() == 0:
                signalon = utime.ticks_us()
                success = True
                break
        if not success:
            duration2 = (utime.ticks_us() - signaloff) / 1000
            self.error_code = 2
            self.error_message = "Failed 2 after " + str(duration2) + " milliseconds"
            return 0
        timepassed = signalon - signaloff
        self.distance = (timepassed * 0.343) / 2
        self.last_distance_measured = self.distance
        return self.distance

class IRSensor(Sensor):
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'INFRA_RED', name)
        self.pin_no = pin_no
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN, machine.Pin.PULL_UP)
        self.type = 'IR'
    
    def get(self):
        if self.pin.value() == 0:
            self.state = 'ON'
        elif self.pin.value() == 1:
            self.state = 'OFF'
        else:
            self.state = 'UNKNOWN'
        return self.state

class Switch(Sensor):
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'SWITCH', name)
        self.pin_no = pin_no
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN, machine.Pin.PULL_UP)
        self.type = 'SWITCH'
    
    def get(self):
        if self.pin.value() == 0:
            self.state = 'ON'
        elif self.pin.value() == 1:
            self.state = 'OFF'
        else:
            self.state = 'UNKNOWN'
        return self.state


class Output(GPIO):
    def __init__(self, pin_no, name, type_code):
        self.pin_no = pin_no
        self.name = name
        self.type_code = type_code
        self.pin = machine.Pin(pin_no, machine.Pin.OUT)
        super().__init__(pin_no, type_code, name)

class LED(Output):
    def __init__(self, pin_no, name):
        super().__init__(pin_no, name, 'LED')
    
    def on(self):
        self.pin.on()
        
    def off(self):
        self.pin.off()


class RGBLED():
    def __init__(self, red_led, green_led, blue_led, name):
        self.red_led = red_led
        self.green_led = green_led
        self.blue_led = blue_led
        self.name = name
        
    def on(self):
        self.red_led.on()
        self.green_led.on()
        self.blue_led.on()

    def red(self):
        self.red_led.on()

    def green(self):
        self.green_led.on()

    def blue(self):
        self.blue_led.on()

    def purple(self):
        self.red_led.on()
        self.blue_led.on()

    def orange(self):
        self.red_led.on()
        self.green_led.on()

    def off(self):
        self.red_led.off()
        self.green_led.off()
        self.blue_led.off()

class GPIOServo(object):
    def __init__(self, pin: int=15, hz: int=50):
        self._servo = PWM(Pin(pin))
        self._servo.freq(hz)
    
    #duty = 1638 = 0.5ms = 65535/2/(T)(1/50)/2*1000
    def ServoDuty(self, duty): 
        if duty <= 1638:              
            duty = 1638
        if duty >= 8190:
            duty = 8190
        self._servo.duty_u16(duty)
        
    def ServoAngle(self, pos): 
        if pos <= 0:
            pos = 0
        if pos >= 180:
            pos = 180
        pos_buffer = (pos/180) * 6552
        self._servo.duty_u16(int(pos_buffer) + 1638)

    def ServoTime(self, us):
        if us <= 500:
            us = 500
        if us >= 2500:
            us = 2500
        pos_buffer= (us / 1000) * 3276
        self._servo.duty_u16(int(pos_buffer))
        
    def deinit(self):
        self._servo.deinit()

###################### CHECK FOR COMPILATION ERRORS
if __name__ == "__main__":
    print ("GPIOPico_v06.py\n")
    test_irsensor = IRSensor(pin_no=22, name='FRONT_LEFT')
    test_button = Button(pin_no=7, name='YELLOW_BUTTON')
    test_volts = Volts(pin_no=29, name='SUPPLY_VOLTS')
    test_ultrasonic = HCSR04(trigger_pin_no=19, echo_pin_no=20, name='FRONT_US', critical_distance=100.0)
    test_switch = Switch(pin_no=13, name='DIP_1')
    test_headlight = RGBLED(LED(10,'LEFT_RED'), LED(14,'LEFT_GREEN'), LED(15,'LEFT_BLUE'),'LEFT_HEADLIGHT')
    # N.B. No GPIO servos on Pico F
    print (test_volts.str_allocated())