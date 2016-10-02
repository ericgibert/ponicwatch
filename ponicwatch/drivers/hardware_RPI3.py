#/bin/python3
"""
    Manage the GPIO port of a Raspberry Pi model 3B and other compatible
    - write on Output pins
    - read input pins

    the tb_hardware.init value is a dictionary identifying the IN and OUT pins

    For sensor:  RPI3.pin
    For switch:

"""
import json
try:
    import pigpio
    _simulation = False
except ImportError:
    _simulation = True
    class sim_pig(object):
        def read(self, pin):
            print("Simulation reading RPI3.%d" % pin)
            return 1
        def write(self, pin, value):
            print("Simulation writing %d to pin RPI3.%d" % (value, pin))

class Hardware_RPI3(object):
    """
    work with the pigpio library: http://abyz.co.uk/rpi/pigpio/python.html
    """

    def __init__(self, pig, in_out):
        """
        :param pig: instance of a pigpio object cretaed by the controller
        :param in_out: JSON string for a dictionary of IN and OUT pins like {"IN": (1,2,3), "OUT":(4,5,6)}
        """
        self.pig = pig
        try:
            self.in_out = json.loads(in_out)
        except json.decoder.JSONDecodeError:
            print("Error: cannot decode the RPI3['init'] dictionary:", in_out)
            exit(-1)
        if _simulation:
            self.pig = sim_pig()
        else:
            for i in self.in_out["IN"]:
                self.pig.set_mode(i, pigpio.INPUT)
            for o in self.in_out["OUT"]:
                self.pig.set_mode(o, pigpio.OUTPUT)
                self.pig.write(o, 0)


    def read(self, pin, param=None):
        return self.pig.read(pin) if pin in self.in_out["IN"] else None


    def write(self, param):
        pin, value = param
        if pin in self.in_out["OUT"]: self.pig.write(pin, value)


    def set_pin_as_input(self, pin):
        """Already done at __init__"""
        # self.pig.set_mode(pin, pigpio.INPUT)
        pass

    def set_pin_as_output(self, pin):
        """Already done at __init__"""
        # self.pig.set_mode(pin, pigpio.OUTPUT)
        pass
