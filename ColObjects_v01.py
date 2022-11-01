module_name = 'ColObjects_v01.py'

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
            self.valid = False
            return None
        self.valid = True
        ColObj.allocated[self.name] = self
        
    def __str__(self):
        return self.name
    
    def close(self):  #  usually overriden
        ColObj.allocated[self.name] = 'FREE'

class Motor(ColObj):
    def __init__(self, name):
        response = super().__init__(name)
        if not self.valid:
            return None
        self.name = name
    def clk(self, speed):
        print ('**** Must be overriden')
    def anti(self, speed):
        print ('**** Must be overriden')
    def stop(self):
        print ('**** Must be overriden')
    def close(self):
        super().close()


if __name__ == "__main__":
    print (module_name)

    test_object_1 = ColObj('testing_1')
    print (ColObj.str_allocated())
    
    test_object_2 = ColObj('testing_2')
    print (ColObj.str_allocated())
    
    test_object_3 = Motor('testing_2')
    if not test_object_3.valid:
        print ('*** name', test_object_3.name, 'already used')
    print (ColObj.str_allocated())
    
    test_object_1.close()
    print (ColObj.str_allocated())
    
    