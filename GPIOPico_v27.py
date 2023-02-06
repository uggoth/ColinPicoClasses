module_name = 'GPIOPico_v27.py'
creation_date = '202302060808'

import ColObjects_v12 as ColObjects
import machine
import utime

#GPIO class reference:
#   GPIO
#      Reserved
#      DigitalInput
#         Button
#         Control Pin
#         IRSensor
#         Switch
#         USEcho
#         Volts
#      DigitalOutput
#         LED
#         USTrigger
#      PWM
#         Buzzer
#         GPIOServo
#   Compound objects with multiple inheritance
#      FIT0441Motor
#      L298Motor
#      HCSR04

class GPIO(ColObjects.ColObj):

    first_pin_no = 0
    last_pin_no = 29
    free_code = 'FREE'
    allocated = [free_code]*(last_pin_no + 1)
    ids = {}

    def allocate(pin_no, obj):
        if ((pin_no < GPIO.first_pin_no) or (pin_no > GPIO.last_pin_no)):
            raise ColObjects.ColError('pin no {} not in range {} to {}'.format(
                pin_no, GPIO.first_pin_no, GPIO.last_pin_no))
        if GPIO.allocated[pin_no] != GPIO.free_code:
            raise ColObjects.ColError('pin no {} already in use'.format(pin_no))
        GPIO.allocated[pin_no] = obj
        return True

    def deallocate(pin_no):
        GPIO.allocated[pin_no] = GPIO.free_code

    def str_allocated():
        out_string = ''
        for i in range(len(GPIO.allocated)):
            if GPIO.allocated[i] == GPIO.free_code:
                out_string += '{:02} : --FREE--'.format(i) + "\n"
            else:
                obj = GPIO.allocated[i]
                out_string += ('{:02}'.format(i) + ' : ' +
                                '{:18}'.format(obj.name) + "\n")
        return out_string
    
    def get_type_list(type_code):
        type_list = {}
        for obj in GPIO.allocated:
            if obj.type_code == type_code:
                type_list[obj.name] = obj
        return type_list

    valid_type_codes = {'INFRA_RED':'INPUT',
                        'BUTTON':'INPUT',
                        'BUZZER':'OUTPUT',
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
                        'MOTOR':'OUTPUT',
                        'NEOPIXEL':'OUTPUT'}
    
    def __init__(self, name, type_code, pin_no):
        super().__init__(name)
        if type_code not in GPIO.valid_type_codes:
            raise ColObjects.ColError (type_code + 'not in' + GPIO.valid_type_codes)
        self.type_code = type_code
        GPIO.allocate(pin_no, self)
        self.pin_no = pin_no
        self.previous = 'UNKNOWN'

    def close(self):
        GPIO.deallocate(self.pin_no)
        super().close()

class Reserved(GPIO):
    def __init__(self, name, type_code, pin_no):
        super().__init__(name, type_code, pin_no)

#############  INPUTS  #############################################################

class DigitalInput(GPIO):
    def __init__(self, name, type_code, pin_no, pullup=machine.Pin.PULL_UP, callback=None):
        super().__init__(name, type_code, pin_no)
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN, pullup)
        if callback is not None:
            self.pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=callback)
        self.state = 'UNKNOWN'
        GPIO.ids[id(self.pin)] = self
    def get(self):
        if self.pin.value() == 0:
            self.state = 'ON'
        elif self.pin.value() == 1:
            self.state = 'OFF'
        else:
            self.state = 'UNKNOWN'
        return self.state

class Button(DigitalInput): 
    button_list = []
    def __init__(self, name, pin_no):
        super().__init__(name, 'BUTTON', pin_no)
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN, machine.Pin.PULL_UP)
        Button.button_list.append(self)
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
            if self.state == 'ON':
                if LED is not None:
                    LED.off()
                return True
            utime.sleep_ms(1)
        if LED is not None:
            LED.off()
        return False
        
class ControlPin(DigitalInput):
    def __init__(self, name, pin_no):
        super().__init__(name, 'CONTROL', pin_no)
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN, machine.Pin.PULL_DOWN)
    def get(self):
        return self.pin.value()

class IRSensor(DigitalInput):
    def __init__(self, name, pin_no, callback=None):
        super().__init__(name, 'INFRA_RED', pin_no, callback=callback)

class Switch(DigitalInput):
    switch_list = []
    def __init__(self, name, pin_no):
        super().__init__(name, 'SWITCH', pin_no)
        self.pin = machine.Pin(self.pin_no, machine.Pin.IN, machine.Pin.PULL_UP)
        Switch.switch_list.append(self)
    def get(self):
        if self.pin.value() == 0:
            self.state = 'ON'
        elif self.pin.value() == 1:
            self.state = 'OFF'
        else:
            self.state = 'UNKNOWN'
        return self.state

class USEcho(DigitalInput):    
    def __init__(self, name, pin_no):
        super().__init__(name, 'US_ECHO', pin_no)

class Volts(DigitalInput):
    def __init__(self, name, pin_no):
        super().__init__(name, 'VOLTS', pin_no)
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

###############  OUTPUTS  #############################################################

class DigitalOutput(GPIO):
    def __init__(self, name, type_code, pin_no):
        super().__init__(name, type_code, pin_no)
        self.pin = machine.Pin(pin_no, machine.Pin.OUT)
    def set(self, new_state):
        if self.new_state == 'ON':
            self.pin.value(0)
            return True
        elif self.new_state == 'OFF':
            self.pin.value(1)
            return True
        return False

class LED(DigitalOutput):
    def __init__(self, name, pin_no):
        super().__init__(name, 'LED', pin_no)    
    def on(self):
        self.pin.on()
    def off(self):
        self.pin.off()

class USTrigger(DigitalOutput):
    def __init__(self, name, pin_no):
        super().__init__(name, 'US_TRIGGER', pin_no)


#############  PWM OUTPUTS  ###########################################################

class PWM(GPIO):
    pwms_by_gpio = ['0A','0B','1A','1B','2A','2B','3A','3B','4A','4B','5A','5B','6A','6B','7A','7B','0A','0B','1A','1B','2A','2B','3A','3B','4A','4B','5A','5B','6A','6B','7A','7B']
    gpios_by_pwm = {'0A':[0,16],'0B':[1,17],'1A':[2,18],'1B':[3,19],'2A':[4,20],'2B':[5,21],'3A':[6,22],'3B':[7,23],'4A':[8,24],'4B':[9,25],'5A':[10,26],'5B':[11,27],'6A':[12,28],'6B':[13,29]}
    pwms_allocated = {}
    def __init__(self, name, type_code, pin_no, freq):
        super().__init__(name, type_code, pin_no)
        self.pin = machine.Pin(pin_no)
        self.pwm = machine.PWM(self.pin)
        self.generator = PWM.pwms_by_gpio[pin_no]
        if self.generator in PWM.pwms_allocated:
            raise ColObjects.ColError('**** PWM generator ' + self.generator + ' already in use')
        PWM.pwms_allocated[self.generator] = pin_no
        self.pwm.freq(freq)
    def set_duty(self, duty):
        self.pwm.duty_u16(duty)
    def close(self):
        self.pwm.deinit()
        del(PWM.pwms_allocated[self.generator])
        super().close()

class Buzzer(ColObjects.ColObj):     # N.B. If 'dip' is supplied, Buzzer only works if DIP is ON.
    def __init__(self, name, pin_no, dip=None):
        self.name = name
        super().__init__(name)
        self.pin_no = pin_no
        self.pwm_object = PWM(name+'_PWM', 'BUZZER', pin_no, 262)
        self.pin = self.pwm_object.pwm
        self.dip = dip
        self.octaves = []    #  Octaves starting at C.  12 tone scales
        self.octaves.append([262,277,294,311,330,349,370,392,415,440,466,494])  #     C, C#, D, D#, E, F, F#, G, G#, A, B♭, B
    def play_note(self, octave, note, milliseconds):  #  milliseconds = 0 is continuous until note_off()
        if ((self.dip != None) and (self.dip.get() == 'ON')):   #  Note suppressed
            return
        octave_index = octave - 1
        if octave_index > len (self.octaves) - 1:
            octave_index = 0
        if octave_index < 0:
            octave_index = 0
        note_index = note - 1
        if note_index > len (self.octaves[octave_index]) - 1:
            note_index = 0
        if note_index < 0:
            note_index = 0
        self.pin.duty_u16(1000)
        frequency = self.octaves[octave_index][note_index]
        #print (frequency)
        self.pin.freq(frequency)
        if milliseconds > 0:
            utime.sleep_ms(milliseconds)
            self.note_off()
    def note_off(self):
        self.pin.duty_u16(0)
    def play_beep(self):
        self.play_note(1, 2, 600)
    def play_ringtone(self):
        song = []
        song.append([3,700])
        song.append([6,300])
        song.append([3,400])
        song.append([9,800])
        for note in song:
            self.play_note(1, note[0], note[1])
    def close(self):
        self.note_off()
        self.pwm_object.close()

    
class GPIOServo(GPIO):
    def __init__(self, name, pin_no: int=15, hertz: int=50):
        super().__init__(name, 'SERVO', pin_no)
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
        
######################  Compound Objects  ###########################

class FIT0441Motor(ColObjects.Motor):
    def __init__(self, name, direction_pin_no, speed_pin_no, pulse_pin_no):
        super().__init__(name)
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
        super().__init__(name)
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

class HCSR04(ColObjects.ColObj):
    def __init__(self,
                 name,
                 trigger_pin_no,
                 echo_pin_no,
                 critical_distance):
        response = super().__init__(name)
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
    def close(self):
        self.trigger_object.close()
        self.echo_object.close()
        super().close()


if __name__ == "__main__":
    print (module_name)
    uart_tx = Reserved('UART TX', 'OUTPUT', 0)
    uart_rx = Reserved('UART RX', 'INPUT', 1)
    smps_mode = Reserved('SMPS Mode', 'OUTPUT', 23)
    vbus_monitor = Reserved('VBUS Monitor','INPUT',24)
    onboard_led = LED('Onboard LED', 25)
    onboard_volts = Volts('Onboard Voltmeter', 29)
    print ('Normally reserved:')
    print (GPIO.str_allocated())


