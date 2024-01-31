module_name = 'GPIOPico_V30.py'
creation_date = '202307141208'

if __name__ == "__main__":
    print (module_name, 'starting')

import ColObjects_V16 as ColObjects
import machine
import utime
import sbus_receiver_3 as sbus_receiver
import _thread

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
#         SBUS Receiver
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
                        'SBUS':'INPUT',
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
        if new_state == 'ON':
            self.pin.value(0)
            return True
        elif new_state == 'OFF':
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

class SBusReceiver(ColObjects.ColObj):
    def __init__(self, tx_pin_no, rx_pin_no, uart_no, throttle_interpolator, steering_interpolator, baud_rate = 100000):
        super().__init__('MicroZone Remote','SBus Remote')
        self.tx_pin_no = 0
        self.rx_pin_no = 1
        self.uart_no = 0
        self.baud_rate = baud_rate
        self.uart_tx = DigitalOutput('UART TX', 'SBUS', tx_pin_no)
        self.uart_rx = DigitalInput('UART RX', 'SBUS', rx_pin_no)
        self.uart = machine.UART(uart_no, baud_rate, tx = machine.Pin(tx_pin_no), rx = machine.Pin(rx_pin_no), bits=8, parity=0, stop=2)
        self.sbus = sbus_receiver.SBUSReceiver(self.uart)
        self.thread_enable = True
        self.joystick_raws = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.thread_running = False
        self.thread = None
        self.throttle_interpolator = throttle_interpolator
        self.steering_interpolator = steering_interpolator

    def __str__(self):
        outstring = self.name + '  ' + self.description
        outstring += ',  UART: ' + str(self.uart_no)
        outstring += ',  TX pin ' + str(self.tx_pin_no)
        outstring += ',  RX pin ' + str(self.rx_pin_no)
        return outstring

    def thread_1_code(self):
        self.thread_running = True
        while True:
            if not self.thread_enable:
                break
            utime.sleep_us(300)
            self.sbus.get_new_data()
            self.joystick_raws = self.sbus.get_rx_channels()[0:5]
        self.thread_running = False

    def run_thread(self):
        self.thread = _thread.start_new_thread(self.thread_1_code, ())

    def stop_thread(self):
        self.thread_enable = False

    def get(self):
        steering_raw = self.joystick_raws[0]
        throttle_raw = self.joystick_raws[2]
        throttle_value = self.throttle_interpolator.interpolate(throttle_raw)
        steering_value = self.steering_interpolator.interpolate(steering_raw)
        return throttle_raw, throttle_value, steering_raw, steering_value
        
    def close(self):
        self.stop_thread()
        self.uart_tx.close()
        self.uart_rx.close()
        super().close()

if __name__ == "__main__":
    print (module_name)
    smps_mode = Reserved('SMPS Mode', 'OUTPUT', 23)
    vbus_monitor = Reserved('VBUS Monitor','INPUT',24)
    onboard_led = LED('Onboard LED', 25)
    onboard_volts = Volts('Onboard Voltmeter', 29)
    print ('Normally reserved:')
    print (GPIO.str_allocated())
    tx_pin_no = 0
    rx_pin_no = 1
    uart_no = 0
    throttle_interpolator = ColObjects.Interpolator('Throttle Interpolator',
                            [100, 201, 1000, 1090, 1801, 2000], [-100.0, -100.0, 0.0, 0.0, 100.0, 100.0])
    steering_interpolator = ColObjects.Interpolator('Steering Interpolator',
                            [100, 393, 1180, 1220, 1990, 2000], [100.0, 100.0, 0.0, 0.0, -100.0, -100.0])
    test_sbus = SBusReceiver(tx_pin_no, rx_pin_no, uart_no, throttle_interpolator, steering_interpolator)
    print (test_sbus)
    print ('--- INSTANTIATED --')
    print (ColObjects.ColObj.str_allocated())
    smps_mode.close()
    vbus_monitor.close()
    onboard_led.close()
    onboard_volts.close()
    test_sbus.close()
    throttle_interpolator.close()
    steering_interpolator.close()
    print ('--- AFTER CLOSE --')
    print (ColObjects.ColObj.str_allocated())
    print (module_name, 'finished')
