module_name = 'NeoPixel_v02.py'

import RemoteControl_v11 as RemoteControl
GPIOPico = RemoteControl.GPIOPico
ColObjects = GPIOPico.ColObjects
import utime
import neopixel

class NeoPixel(GPIOPico.Output):
    def __init__(self, name, pin_no, no_pixels, mode):
        super().__init__(name, 'NEOPIXEL', pin_no)
        self.valid = False
        self.state_machine_no = RemoteControl.StateMachine.allocate(self)
        self.no_pixels = no_pixels
        self.mode = mode
        self.pixels = neopixel.Neopixel(self.no_pixels, self.state_machine_no, self.pin_no, self.mode)
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.blue = (0, 0, 255)
        self.white = (255,255,255)
        self.off = (0,0,0)
        self.patterns = [[self.off, self.off, self.red, self.green, self.blue, self.off, self.off],
                         [self.off, self.red, self.red, self.blue, self.blue, self.off, self.off],
                         [self.off, self.off, self.green, self.green, self.blue, self.blue, self.off]]

    def clear(self):
        self.pixels.clear()
        self.pixels.show()

    def close(self):
        self.clear()
        RemoteControl.StateMachine.deallocate(self.state_machine_no)
        super().close()

    def show_ring(self, centre, start, pattern_in=0):
        pattern_no = pattern_in % len(self.patterns)
        self.pixels[0] = centre
        for i in range(self.no_pixels-1):
            self.pixels[i+1] = self.patterns[pattern_no][(start+i+1)%len(self.patterns[pattern_no])]
        self.pixels.show()

if __name__ == "__main__":
    print (module_name)

