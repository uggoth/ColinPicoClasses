module_name = 'ColObjects_v03.py'

class ColError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ColObj():
    
    allocated = {}
    
    def str_allocated():
        out_string = ('{:18}'.format('NAME') +
                        '{:18}'.format('OBJECT') + '\n')
        for name in sorted(ColObj.allocated):
            if ColObj.allocated[name] != 'FREE':
                obj = ColObj.allocated[name]
                out_string += ('{:18}'.format(obj.name)  +
                                str(obj) + '\n')
        return out_string
    
    def __init__(self, name):
        self.name = name
        if name in ColObj.allocated:
            raise ColError(name + ' already allocated')
        ColObj.allocated[self.name] = self
        
    def __str__(self):
        return self.name
    
    def close(self):
        ColObj.allocated[self.name] = 'FREE'


class Motor(ColObj):
    def __init__(self, name):
        super().__init__(name)
    def clk(self, speed):
        raise ColError('**** Must be overriden')
    def anti(self, speed):
        raise ColError('**** Must be overriden')
    def stop(self):
        raise ColError('**** Must be overriden')
    def close(self):
        super().close()


if __name__ == "__main__":
    print (module_name)
   
    