from machine import Pin
import utime
import rp2

@rp2.asm_pio()
def measure():
    wrap_target()
    wait(0,pin,0)  #  don't start in the middle of a pulse
    wait(1,pin,0)
    mov(x,invert(null))
    label('loop')
    jmp(x_dec,'pin_on') #  Note: x will never be zero. We just want the decrement
    nop()
    label('pin_on')
    jmp(pin, 'loop')
    mov(isr,invert(x))  #  Note: It's a FIFO stack (i.e. a queue). We would prefer LIFO
    push(noblock)
    wrap()

class StateMachine():
    def __init__(self, name, state_machine_no, pin_no, hertz=100000):
        self.name = name
        self.state_machine_no = state_machine_no
        self.pin_no = pin_no
        self.hertz = hertz
        self.pin = Pin(pin_no, Pin.IN, Pin.PULL_DOWN)
        self.instance = rp2.StateMachine(self.state_machine_no, measure, freq=self.hertz, in_base=self.pin, jmp_pin=self.pin)
        self.instance.active(1)
        while not self.instance.rx_fifo():
            utime.sleep_ms(1)
        self.x = self.instance.get()
    def get_next_blocking(self):
        self.x =  self.instance.get()
        return self.x
    def get_latest(self):
        while self.instance.rx_fifo():
            self.x = self.instance.get()
        return self.x
    def close(self):
        self.instance.active(0)
