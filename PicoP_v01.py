module_name = 'PicoP_v01.py'

import NeoPixel_v09 as NeoPixel
GPIOPico = NeoPixel.GPIOPico
import utime

class ThisStrip(NeoPixel.NeoPixel):
    def __init__(self):
        super().__init__(name='Helmet Strip', pin_no=2, no_pixels=104, mode='GRB')
        self.sectors['warning'] = [0,0]
        self.sectors['back_left'] = [1,13]
        self.sectors['left'] = [14,37]
        self.sectors['front'] = [38,67]
        self.sectors['right'] = [68,89]
        self.sectors['back_right'] = [90,103]
        self.sectors['all'] = [1,103]

class TheseButtons():
    def __init__(self):
        self.red_button = GPIOPico.Button('Red Button', 14)
        self.green_button = GPIOPico.Button('Green Button', 15)

class TheseSwitches():
    def __init__(self):
        self.dip_1 = GPIOPico.Switch('DIP 1', 11)
        self.dip_2 = GPIOPico.Switch('DIP 2', 12)
        self.dip_3 = GPIOPico.Switch('DIP 3', 13)

if __name__ == "__main__":
    print (module_name)
