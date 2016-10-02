#/bin/python3
"""

16 I/O Expander on I2C bus
- Bank A is defined as 8 Inputs
- Bank B is defined as 8 Outputs

"""
from .MCP23017 import IC_MCP23017

class Hardware_MCP23017(object):
    """Created by a controller"""

    def __init__(self, pig, i2c_addr=0x20, bus=1):
        """
        Wrapper aroung the integrated circuit MCP23017
        :param pig: controller's pigpio access
        :param bus: I2C bus
        :param address: I2C address defined by IC pins 15,16,17 (0x20 when all 3 are grounded)
        """
        self.pig = pig
        self.bus, self.i2c_addr = bus, i2c_addr
        self.IC = IC_MCP23017(pig, address=self.i2c_addr, num_gpios=16, busnum=self.bus)

    def read(self, pin, param=None):
        """
        Read the pin value
        :param pin: pin number 0-15
        :param param: ignored for this chip
        :return: 0.0 or 1.0 for both read_value and calculated_value
        """
        value = float(self.IC.input(int(pin)))
        return (value, value)

    def write(self, param):
        """
        Write value (0,1) to the pin
        :param param: tuple (pin, value)
        :return:
        """
        pin, value = param
        self.IC.output(pin, value)

    def cleanup(self):
        self.IC.cleanup()

    def set_pin_mode(self, pin, value):
        self.IC.set_pin_mode(pin, value)