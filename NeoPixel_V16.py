module_name = 'NeoPixel_V16.py'   #  11/Aug/2023

import GPIOPico_V30 as GPIOPico
ColObjects = GPIOPico.ColObjects
import neopixel
import machine
import utime

class NeoPixel(GPIOPico.Reserved):
    def __init__(self, name, pin_no, no_pixels, mode):
        super().__init__(name, 'NEOPIXEL', pin_no)
        self.valid = False
        #  On Pico W the wireless uses state machine 4 in block 1
        self.block_no = 1   # Conventionally for neopixels
        self.state_machine = ColObjects.PIO(name+'_PIO',self.block_no)
        self.state_machine_no = self.state_machine.pio_no
        #GPIOPico.GPIO.allocate(pin_no, self)
        self.no_pixels = no_pixels
        self.mode = mode
        self.pixels = neopixel.Neopixel(self.no_pixels, self.state_machine_no, self.pin_no, self.mode)
        #  The following definitions are examples which can be overriden or augmented
        self.colours = {'red':(255, 0, 0),
                        'dim_red':(63,0,0),
                        'orange':(255, 45, 0),
                        'yellow':(200,130,0),
                        'green':(0, 255, 0),
                        'dim_green':(0,63,0),
                        'blue':(0, 0, 255),
                        'white':(255,255,255),
                        'dim_white':(63,63,63),
                        'on':(255,255,255),
                        'off':(0,0,0)}
        self.patterns = {'off':['off'],
                         'on':['white'],
                         'red':['red'],
                         'orange':['orange'],
                         'blue':['blue'],
                         'mixed':['red','blue','green','white']}
        self.sectors = {}

    def __str__(self):
        return (self.name + '  pixels:' + str(self.no_pixels))

    def set_sector_to_pattern(self, sector, pattern, offset=0):
        start = self.sectors[sector][0]
        end = self.sectors[sector][1]
        slen = end - start + 1
        plen = len(self.patterns[pattern])
        j = 0
        for i in range(slen):
            where = start + ((i + offset) % slen)
            colour = self.colours[self.patterns[pattern][j]]
            self.pixels[where] = colour
            j += 1
            j = j % plen

    def set_pixel(self, where, colour):
        self.pixels[where] = self.colours[colour]
        self.pixels.show()

    def fill(self, colour_code):
        colour = self.colours[colour_code]
        print (colour_code, colour)
        self.pixels.fill(colour)
        self.pixels.show()

    def fill_sector(self, sector, colour):
        start = self.sectors[sector][0]
        end = self.sectors[sector][1]
        self.pixels[start:end+1] = self.colours[colour]
        self.pixels.show()

    def show(self):
        self.pixels.show()
        
    def clear(self):
        self.pixels.clear()
        self.pixels.show()

    def close(self):
        self.clear()
        utime.sleep_ms(100)
        super().close()
        utime.sleep_ms(100)
        self.state_machine.close()

    def on(self, colour=(120, 100, 0)):
        self.pixels.fill(colour)
        self.pixels.show()
    
    def off(self):
        self.clear()

if __name__ == "__main__":
    print (module_name)
    dummy = NeoPixel(name='TEST', pin_no=18, no_pixels=14, mode='GRB')
    dummy.on()
    print (ColObjects.PIO.str_allocated())
    utime.sleep(2)
    dummy.off()
    dummy.close()

