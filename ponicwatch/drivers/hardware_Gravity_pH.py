#!/bin/env python
"""
    Reads the signal provided by the Gravity pH probe

    https://www.dfrobot.com/product-1025.html

    Requires a ADC to read the voltage from the signal pin

    Declaration in the database: tb_hardware.hardware == GRAVITY_pH
"""


class Hardware_Gravity_pH(object):
    """
      Connection on +5V and Ground + signal on ADC pin
    """

    def __init__(self, pig, init_dict, MCP3208=None):
        """

        :param pig: instance of a pigpio object created by the controller
        :param init_dict: parameters provided at initialization time
                { "MCP3208": 5, "pin": 1 }
                - MCP3208: the tb_hardware.id of the MCP3208 the probe is connected too
                - pin: the MCP3208's pin
        :param MCP3208: only for testing - provide the MCP3208 PWO
        """
        self.pig = pig
        self.MCP3208 = MCP3208 or self.pig.get_pwo("Hardware", init_dict["MCP3208"])
        self.pin = init_dict["pin"]

    def read(self, pin=None, param=5.0):
        """Reads the voltage and convert to pH
            param is the reference voltage
        """
        data, volts12bits = self.MCP3208.average(channel=self.pin, samples=10, param=param)
        return data, volts12bits * 3.5 # coefficient from documentation

if __name__ == "__main__":
    import pigpio
    from hardware_MCP3208 import Hardware_MCP3208
    from time import sleep
    pig = pigpio.pi()
    mcp3208 = Hardware_MCP3208(pig, { "channel": 0, "baud": 50000, "flags":0 })
    gravity_pH = Hardware_Gravity_pH(pig, init_dict={ "pin": 0}, MCP3208=mcp3208)
    try:
        while True:
            data, pH = gravity_pH.read()
            print("Read: {} , converted as pH={:.2f}".format(data, pH))
            sleep(2)
    finally:
        mcp3208.cleanup()
