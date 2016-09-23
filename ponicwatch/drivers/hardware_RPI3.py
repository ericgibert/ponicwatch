#/bin/python3
"""
    Manage the GPIO port of a Raspberry Pi model 3B and other compatible
    - write on Output pins
    - read input pins

    the tb_hardware.init value is a dictionary identifying the IN and OUT pins

    For sensor:  RPI3._.pin
    For switch:

"""
from json import loads
try:
    import pigpio
    _simulation = False
except ImportError:
    _simulation = True

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
        self.in_out = loads(in_out)
        for i in self.in_out["IN"]:
            self.pig.set_mode(i, pigpio.INPUT)
        for o in self.in_out["OUT"]:
            self.pig.set_mode(o, pigpio.OUTPUT)
            self.pig.write(o, 0)


    def read(self, pin):
        return self.pig.read(pin) if pin in self.in_out["IN"] else None


    def write(self, pin, value):
        if pin in self.in_out["OUT"]: self.pig.write(pin, value)
