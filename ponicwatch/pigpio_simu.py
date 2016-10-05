"""
  Simulation of the pigpio function to test on a NON Raspi hardware
"""
from random import randint

class pi():
    connected = False
    def __init__(self):
        print("INFO --> PIGPIO simulation activated")
        self.inter_pin = None

    def i2c_open(self, busnum, address):
        return 1

    def i2c_read_byte_data(self, handle, register):
        sim = randint(0, 255)
        print("Simulation read byte pigpio", sim, "from register", register)
        return sim

    def i2c_write_byte_data(self, handle, register, value):
        print("Simulation write byte pigpio", value, "on register", register)

    def read(self, pin, param=None):
        data = randint(0, 1)
        print("Simulation reading RPI3.%d [%d]" % (pin, data))
        return data

    def write(self, pin, value):
        print("Simulation writing %d to pin RPI3.%d" % (value, pin))

    def set_watchdog(self, pin, value):
        pass

    def set_pull_up_down(self, pin, value):
        pass

    def callback(self, pin, edge, func):
        self.inter_pin = pin
        self.func = func

    def set_mode(self, pin, value):
        pass