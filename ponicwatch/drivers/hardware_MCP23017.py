#/bin/python3
"""

16 I/O Expander on I2C bus
- Bank A is defined as 8 Inputs
- Bank B is defined as 8 Outputs

"""

class Hardware_MCP23017(object):
    """Created by a controller"""

    def __init__(self, pig, bus=1, i2c_addr=0x20):
        """

        :param pig: controller's pigpio access
        :param bus: I2C bus
        :param address: I2C address defined by IC pins 15,16,17 (0x20 when all 3 are grounded)
        """
        self.pig = pig
        self.bus, self.i2c_addr = bus, i2c_addr
