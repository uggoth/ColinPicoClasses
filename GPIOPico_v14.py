module_name = 'GPIOPico_v14.py'

import ColObjects_v01 as ColObjects
import machine
import utime

class GPIO(ColObjects.ColObj):

    allocated = ['FREE']*40

    valid_type_codes = {'INFRA_RED':'INPUT',
                        'BUTTON':'INPUT',
                        'US_TRIGGER':'OUTPUT',
                        'US_ECHO':'INPUT',
                        'SWITCH':'INPUT',
                        'VOLTS':'INPUT',
                        'ADC':'INPUT',
                        'LED':'OUTPUT',
                        'CONTROL':'INPUT',
                        'INPUT':'INPUT',
                        'OUTPUT':'OUTPUT',
                        'SERVO':'OUTPUT',
                        'MOTOR':'OUTPUT'}
    allocated_by_type = {}
    for type_code in valid_type_codes:
        allocated_by_type[type_code] = {}
    
    def __init__(self, name, type_code, pin_no):
        response = super().__init__(name)
        if not self.valid:
            return None
        self.valid = False
        first_pin_no = 0
        last_pin_no = len(GPIO.allocated) - 1
        if first_pin_no <= int(pin_no) <= last_pin_no:
            if GPIO.allocated[pin_no] == 'FREE':
                if type_code not in GPIO.valid_type_codes:
                    print (type_code, 'not in', GPIO.valid_type_codes)
                    return None
            else:
                print (pin_no,'already allocated to ',GPIO.allocated[pin_no].name)
                return None
        else:
            print (pin_no,'not in range',first_pin_no,'to',last_pin_no)
            return None
        self.valid = True
        self.pin_no = pin_no
        self.previous = 'UNKNOWN'
        GPIO.allocated[self.pin_no] = self
        GPIO.allocated_by_type[self.type_code][self.pin_no] = self

    def close(self):
        GPIO.deallocate(self.pin_no)
        super().close()

    def str_allocated():
        out_string = ''
        for i in range(len(GPIO.allocated)):
            if GPIO.allocated[i] != 'FREE':
                obj = GPIO.allocated[i]
                out_string += ('{:02}'.format(i) + ' : ' +
                                '{:18}'.format(obj.name) + ' : ' +
                                str(obj) + "\n")
        return out_string
    
    def deallocate(pin_no):
        GPIO.allocated[pin_no] = 'FREE'

class Output(GPIO):
    def __init__(self, name, type_code, pin_no):
        super().__init__(name, type_code, pin_no)
        if self.valid:
            self.pin_no = pin_no
            self.type_code = type_code
            self.pin = machine.Pin(pin_no, machine.Pin.OUT)
        else:
            return None

class LED(Output):
    def __init__(self, name, pin_no):
        super().__init__(name, 'LED', pin_no)
    
    def on(self):
        self.pin.on()
        
    def off(self):
        self.pin.off()

class FIT0441Motor(ColObjects.Motor):
    def __init__(self, name, direction_pin_no, speed_pin_no, pulse_pin_no):
        response = super().__init__(name)
        if not self.valid:
            return None
        self.direction_pin_GPIO = GPIO(pin_no=direction_pin_no, type_code='MOTOR', name=name+'_direction_'+str(direction_pin_no))
        self.direction_pin = machine.Pin(direction_pin_no, machine.Pin.OUT)
        self.speed_pin_GPIO = GPIO(pin_no=speed_pin_no, type_code='MOTOR', name=name+'_speed_'+str(speed_pin_no))
        self.speed_pin = machine.PWM(machine.Pin(speed_pin_no))
        self.pulse_pin_GPIO = GPIO(pin_no=pulse_pin_no, type_code='MOTOR', name=name+'_pulse_'+str(pulse_pin_no))
        self.pulse_pin = machine.Pin(pulse_pin_no, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pulse_pin.irq(self.pulse_detected)
        self.pulse_count = 0
        self.pulse_checkpoint = 0
        self.duty = 0
        self.stop_duty = 65534
        self.min_speed_duty = 59000
        self.max_speed_duty = 0
        self.clockwise = 1
        self.anticlockwise = 0

    def clk(self, speed):
        self.direction_pin.value(self.clockwise)
        self.set_speed(speed)

    def anti(self, speed):
        self.direction_pin.value(self.anticlockwise)
        self.set_speed(speed)

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
        utime.sleep_ms(1)
        
    def close(self):
        self.deinit()
        utime.sleep_ms(5)
        super().close()

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

class L298NMotor(ColObjects.Motor):
    def __init__(self, name, clk_pin_no, anti_pin_no):
        response = super().__init__(name)
        if not self.valid:
            return None
        #  clk is clockwise looking at the motor from the wheel side
        self.stop_duty = 0
        self.max_speed = 100  #  as an integer percentage
        self.min_speed = 0
        self.min_speed_duty = 0
        self.max_speed_duty = 65534
        self.speed = self.min_speed
        self.freq = 25000
        self.clk_pin_GPIO = GPIO(pin_no=clk_pin_no, type_code='MOTOR', name=name+'_clk_'+str(clk_pin_no))
        self.clk_pin = machine.Pin(clk_pin_no)
        self.clk_PWM = machine.PWM(self.clk_pin)
        self.clk_PWM.freq(self.freq)
        self.clk_PWM.duty_u16(self.stop_duty)
        self.anti_pin_GPIO = GPIO(pin_no=anti_pin_no, type_code='MOTOR', name=name+'_anti_'+str(anti_pin_no))
        self.anti_pin = machine.Pin(anti_pin_no)
        self.anti_PWM = machine.PWM(self.anti_pin)
        self.anti_PWM.freq(self.freq)
        self.anti_PWM.duty_u16(self.stop_duty)
    def convert_speed_to_duty(self, speed):
        duty = int((self.max_speed_duty - self.min_speed_duty) / 100 * speed)
        return duty
    def clk(self, speed):
        self.anti_PWM.duty_u16(self.stop_duty)
        self.clk_PWM.duty_u16(self.convert_speed_to_duty(speed))
    def anti(self, speed):
        self.clk_PWM.duty_u16(self.stop_duty)
        self.anti_PWM.duty_u16(self.convert_speed_to_duty(speed))
    def stop(self):
        self.clk_PWM.duty_u16(self.stop_duty)
        self.anti_PWM.duty_u16(self.stop_duty)
    def close(self):
        self.clk_PWM.deinit()
        self.anti_PWM.deinit()
        utime.sleep_ms(5)
        self.clk_pin_GPIO.close()
        self.anti_pin_GPIO.close()
        super().close()

class Sensor(GPIO):
    def __init__(self, name, type_code, pin_no):
        super().__init__(name, type_code, pin_no)
        if not self.valid:
            return
        self.state = 'UNKNOWN'

class ControlPin(Sensor):
    def __init__(self, name, pin_no):
        super().__init__(name, 'CONTROL', pin_no)
        self.pin_no = pin_no
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN, machine.Pin.PULL_DOWN)
    def get(self):
        return self.pin.value()

class Button(Sensor):
    def __init__(self, name, pin_no):
        super().__init__(name, pin_no, 'BUTTON')
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
    def __init__(self, name, pin_no):
        super().__init__(name, 'VOLTS', pin_no)
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
    def __init__(self, name, pin_no):
        super().__init__(name, pin_no, 'US_TRIGGER')
        self.pin_no = pin_no
        self.pin = machine.Pin(self.pin_no, machine.Pin.OUT)
        self.valid = True

class USEcho(Sensor):    
    def __init__(self, name, pin_no):
        super().__init__(name, pin_no, 'US_ECHO')
        self.pin_no = pin_no
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN)
        self.valid = True


class HCSR04(ColObjects.ColObj):
    def __init__(self,
                 name,
                 trigger_pin_no,
                 echo_pin_no,
                 critical_distance):
        response = super().__init__(name)
        if not self.valid:
            return None
        self.type = 'HCSR04'
        self.trigger_object = USTrigger(name + '_TRIGGER', trigger_pin_no)
        self.trigger = self.trigger_object.pin
        self.echo_object = USEcho(name + '_ECHO', echo_pin_no)
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
    def __init__(self, name, pin_no):
        super().__init__(name, pin_no, 'INFRA_RED')
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
    def __init__(self, name, pin_no):
        super().__init__(name, pin_no, 'SWITCH')
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


class RGBLED(ColObjects.ColObj):
    def __init__(self, name, red_led, green_led, blue_led):
        response = super().__init__(name)
        if not self.valid:
            return None
        self.red_led = red_led
        self.green_led = green_led
        self.blue_led = blue_led
        
    def on(self):
        self.red_led.on()
        self.green_led.on()
        self.blue_led.on()

    def red(self):
        self.red_led.on()
        self.green_led.off()
        self.blue_led.off()

    def green(self):
        self.red_led.off()
        self.green_led.on()
        self.red_led.off()

    def blue(self):
        self.red_led.off()
        self.green_led.off()
        self.blue_led.on()

    def purple(self):
        self.red_led.on()
        self.green_led.off()
        self.blue_led.on()

    def orange(self):
        self.red_led.on()
        self.green_led.on()

    def off(self):
        self.red_led.off()
        self.green_led.off()
        self.blue_led.off()

class GPIOServo(GPIO):
    def __init__(self, name, pin_no: int=15, hertz: int=50):
        super().__init__(name, 'SERVO', pin_no)
        if self.valid:
            self.pin_no = pin_no
            self.hertz = hertz
            self.pin = machine.PWM(machine.Pin(pin_no))
            self.pin.freq(hertz)
    
    #duty = 1638 = 0.5ms = 65535/2/(T)(1/50)/2*1000
    def ServoDuty(self, duty): 
        if duty <= 1638:              
            duty = 1638
        if duty >= 8190:
            duty = 8190
        self.pin.duty_u16(duty)
        
    def ServoAngle(self, pos): 
        if pos <= 0:
            pos = 0
        if pos >= 180:
            pos = 180
        pos_buffer = (pos/180) * 6552
        self.pin.duty_u16(int(pos_buffer) + 1638)

    def ServoTime(self, us):
        if us <= 500:
            us = 500
        if us >= 2500:
            us = 2500
        pos_buffer= (us / 1000) * 3276
        self.pin.duty_u16(int(pos_buffer))
        
    def close(self):
        self.pin.deinit()
        super().close()
        

class Reserved(GPIO):
    def __init__(self, name, type_code, pin_no):
        super().__init__(name, type_code, pin_no)

uart_tx = Reserved('UART TX', 'OUTPUT', 0)
uart_rx = Reserved('UART RX', 'INPUT', 1)
smps_mode = Reserved('SMPS Mode', 'OUTPUT', 23)
vbus_monitor = Reserved('VBUS Monitor','INPUT',24)
onboard_led = LED('Onboard LED', 25)
adc26 = Reserved('ADC 26', 'ADC', 26)
adc27 = Reserved('ADC 27', 'ADC', 27)
adc28 = Reserved('ADC 28', 'ADC', 28)
onboard_volts = Volts('Onboard Voltmeter', 29)

if __name__ == "__main__":
    print (module_name)
    print (' ')
    print ('------ Allocated GPIOs ---------')
    print (GPIO.str_allocated())
    dummy1 = LED('failing',45)
    dummy2 = GPIOServo('testing', 2)
    print (GPIO.str_allocated())
    dummy2.close()
    print (GPIO.str_allocated())


