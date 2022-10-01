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
                        'LED':'OUTPUT'}
    allocated = {}
    allocated_by_type = {}
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
        GPIO.allocated[self.pin_no] = self
        GPIO.allocated_by_type[self.type_code][self.pin_no] = self
        self.name = name
        self.valid = True
        self.previous = 'UNKNOWN'


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
        
    def get(self):
        if self.pin.value() == 0:
            self.state = 'ON'
        elif self.pin.value() == 1:
            self.state = 'OFF'
        else:
            self.state = 'UNKNOWN'
        return self.state
        

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

class ThisVolts(Volts):
    def __init__(self):
        super().__init__(29, 'VIN')

class USTrigger(Sensor):
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'US_TRIGGER', name)
        self.pin = machine.Pin(pin_no, machine.Pin.OUT)

class USEcho(Sensor):    
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'US_ECHO', name)
        self.pin = machine.Pin(pin_no, machine.Pin.IN)

class HCSR04():
    def __init__(self, name,
                 trigger_pin_no,
                 echo_pin_no,
                 critical_distance):
        self.type = 'HCSR04'
        self.name = name
        self.trigger = USTrigger(trigger_pin_no, name + '_TRIGGER').pin
        self.echo = USEcho(echo_pin_no, name + '_ECHO').pin
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

class ThisHCSR04(HCSR04):
    def __init__(self):
        super().__init__(name='FRONT_US',
                 trigger_pin_no=19,
                 echo_pin_no=20,
                 critical_distance=100.0)


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


class TheseIRSensors():
    def __init__(self):
        self.front_left_ir = IRSensor(18,'FRONT_LEFT_IR')
        self.front_right_ir = IRSensor(22,'FRONT_RIGHT_IR')


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


class TheseSwitches():
    def __init__(self):
        DIP_1 = Switch(13,'DIP_1')
        DIP_2 = Switch(12,'DIP_2')
        DIP_3 = Switch(11,'DIP_3')


class LED(GPIO):
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'LED', name)
        if not self.valid:
            return
        self.pin_no = pin_no
        self.name = name
        self.pin = machine.Pin(pin_no, machine.Pin.OUT)
    
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

class LeftHeadlight:
    def __init__(self):
        self.red = LED(10,'LEFT_RED')
        self.green = LED(14,'LEFT_GREEN')
        self.blue = LED(15,'LEFT_BLUE')
        self.headlight = RGBLED(self.red, self.green, self.blue,'LEFT_HEADLIGHT')

class RightHeadlight:
    def __init__(self):
        self.red = LED(27,'RIGHT_RED')
        self.green = LED(26,'RIGHT_GREEN')
        self.blue = LED(17,'RIGHT_BLUE')
        self.headlight = RGBLED(self.red, self.green, self.blue,'RIGHT_HEADLIGHT')


class Output(GPIO):
    def __init__(self, pin_no, type_code, name):
        super().__init__(pin_no, type_code, name)

class FIT0441Direction(Output):
    def __init__(self, pin_no, name):
        super().__init__(pin_no, 'FIT0441_DIRECTION', name)

class FIT0441Motor():
    def __init__(self, name, direction_pin, speed_pin, pulse_pin):
        super().__init__(name)
        self.direction_pin = direction_pin
        self.speed_pin = speed_pin
        self.pulse_pin = pulse_pin
        self.pulse_pin.irq(self.pulse_detected)
        self.pulse_count = 0
        self.pulse_checkpoint = 0
        self.duty = 0
        self.stop_duty = 65534
        self.min_speed_duty = 59000
        self.max_speed_duty = 0
        self.clockwise = 1
        self.anticlockwise = 0
        self.name = 'Unknown'

    def set_pulse_checkpoint(self):
        self.pulse_checkpoint = self.get_pulses()

    def get_pulse_checkpoint(self):
        return self.pulse_checkpoint

    def get_pulse_diff(self):
        return self.get_pulses() - self.pulse_checkpoint

    def deinit(self):
        self.speed_pin.deinit()

    def stop(self):
        duty = self.stop_duty
        self.speed_pin.duty_u16(duty)

    def pulse_detected(self, sender):
        self.pulse_count += 1

    def get_pulses(self):
        return self.pulse_count

    def set_speed(self, speed):  #  as a percentage
        self.duty = (self.min_speed_duty
                     - int(float(self.min_speed_duty - self.max_speed_duty)
                        * (float(speed) / 100.0)))
        self.speed_pin.duty_u16(self.duty)
    
    def set_direction(self, direction):  # 1 = clockwise, 0 = anticlockwise
        if direction == 1:
            self.direction_pin.value(self.clockwise)
        elif direction == 0:
            self.direction_pin.value(self.anticlockwise)

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

