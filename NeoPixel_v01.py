module_name = 'NeoPixel_v01.py'

import ColObjects_v01 as ColObjects
import GPIOPico_v15 as GPIOPico
import RemoteControl_v09 as RemoteControl
import utime
import neopixel

class NeoPixel(GPIOPico.Output):
    def __init__(self, name, pin_no, no_pixels, mode):
        super().__init__(name, 'NEOPIXEL', pin_no)
        if not self.valid:
            return None
        self.valid = False
        self.state_machine_no = RemoteControl.StateMachine.allocate(self)
        if self.state_machine_no is None:
            return None
        self.no_pixels = no_pixels
        self.mode = mode
        self.pixels = neopixel.Neopixel(self.no_pixels, self.state_machine_no, self.pin_no, self.mode)

    def close(self):
        self.pixels.clear()
        self.pixels.show()
        super().close()
        RemoteControl.StateMachine.deallocate(self.state_machine_no)

    def show_ring(self, start, action):
        pixels = self.pixels
        if action == 'OFF':
            pixels.clear()
            pixels.show()
            return
        red = (255, 0, 0)
        green = (0, 255, 0)
        blue = (0, 0, 255)
        white = (255,255,255)
        off = (0,0,0)
        pixels[0] = white
        pattern = [off,red,off,green,off,blue]
        #print ((start+0)%7,(start+5)%6)
        pixels[1] = pattern[(start+0)%6]
        pixels[2] = pattern[(start+1)%6]
        pixels[3] = pattern[(start+2)%6]
        pixels[4] = pattern[(start+3)%6]
        pixels[5] = pattern[(start+4)%6]
        pixels[6] = pattern[(start+5)%6]
        pixels.show()

if __name__ == "__main__":
    print (module_name)

    for i in range(10):
        GPIOPico.onboard_led.on()
        utime.sleep(0.2)
        GPIOPico.onboard_led.off()
        utime.sleep(0.1)

    name = 'Test Ring'
    pin_no = 27
    no_pixels = 7
    mode = 'GRB'
    my_ring = NeoPixel(name, pin_no, no_pixels, mode)
    my_ring.show_ring(start=2, mode='ON')
    utime.sleep_ms(1000)
    my_ring.show_ring(start=2, mode='OFF')
    my_ring.close()
    