"""
  Simulation of the pigpio function to test on a NON Raspi hardware
"""
from random import randint

class pi():
    def __init__(self):
        print("INFO --> PIGPIO simulation activated")

    def i2c_open(self, busnum, address):
        return 1

    def i2c_read_byte_data(self, handle, register):
        sim = randint(0, 255)
        print("Simulation read byte pigpio", sim, "from register", register)
        return sim

    def i2c_write_byte_data(self, handle, register, value):
        print("Simulation write byte pigpio", value, "on register", register)

    def callback(self, interrupt, func):
        pass

    def read(self, pin):
        print("Simulation reading RPI3.%d" % pin)
        return randint(0, 1)

    def write(self, pin, value):
        print("Simulation writing %d to pin RPI3.%d" % (value, pin))

    def set_watchdog(self, pin, value):
        pass

    def set_pull_up_down(self, pin, value):
        pass

    def callback(self, pin, edge, func):
        pass

    def set_mode(self, pin, value):
        pass