#/bin/python3
"""
    Manage the GPIO port of a Raspberry Pi model 3B and other compatible
    - write on Output pins
    - read input pins
    - catch interruption

    the tb_hardware.init value is a dictionary identifying the IN and OUT pins

    For sensor:  RPI3.pin
    For switch:

"""
try:
    import pigpio
    _simulation = False
except ImportError:
    _simulation = True
    class pigpio():
        INPUT=1
        OUTPUT=0
        PUD_DOWN=0
        RISING_EDGE=1

CALLBACKS = {}   # dictionary keeping the functions to callback (value list) when an interrupt is received on the pin (key)

class Hardware_RPI3(object):
    """
    work with the pigpio library: http://abyz.co.uk/rpi/pigpio/python.html
    """

    def __init__(self, pig, init_dict, debug=0):
        """
        :param pig: instance of a pigpio object cretaed by the controller
        :param init_dict: dictionary of IN and OUT pins like {"IN":[],"OUT":[27,9]} and other parameters
        """
        global CALLBACKS
        self.pig = pig
        self.init_dict = init_dict
        self.debug = max(debug, init_dict.get("debug", 0))
        for i in self.init_dict["IN"]:
            self.pig.set_mode(i, pigpio.INPUT)
            self.pig.set_pull_up_down(i, pigpio.PUD_DOWN)
        for o in self.init_dict["OUT"]:
            self.pig.set_mode(o, pigpio.OUTPUT)
            self.pig.write(o, 0)
        try:
            for i in self.init_dict["INTER"]:
                self.pig.callback(i, pigpio.RISING_EDGE, self.pigpio_callback)
        except KeyError:
            # no interruptions
            pass

    def read(self, pin, param=None):
        if param == 'T':
            data = self.read_cpu_temperature()
        else:
            data = float(self.pig.read(pin)) if pin in self.init_dict["IN"] else None
        return data, data

    def write(self, pin, value):
        if pin in self.init_dict["OUT"]:
            self.pig.write(pin, value)
        return self.pig.read(pin)

    def set_pin_as_input(self, pin):
        """Already done at __init__"""
        # self.pig.set_mode(pin, pigpio.INPUT)
        pass

    def set_pin_as_output(self, pin):
        """Already done at __init__"""
        # self.pig.set_mode(pin, pigpio.OUTPUT)
        pass

    def read_cpu_temperature(self):
        """Reads the CPU temperature
        init:  { "IC":"RPI3", "pin":-1, "hw_param":"T"}
        """
        with open('/sys/class/thermal/thermal_zone0/temp', "rt") as tFile:
            tempC = float(tFile.read())
        return tempC / 1000.0

    @staticmethod
    def pigpio_callback(gpio, level, tick):
        """
        Callback when Raspberry Pi 'gpio' pin receives an interrupt
        Need to wire the INTA to that pin
        """
        print("****  PGPIO Interrupt   ****", gpio, level, tick)
        if gpio in CALLBACKS:
            for func in CALLBACKS[gpio]:
                func()

    def get_callbacks(self):
        return CALLBACKS