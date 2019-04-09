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

    def __init__(self, pig, init_dict, ADC=None, debug=0):
        """
        Reads on the ADC the voltage given by the probe.
        Converts the voltage to pH reading.
        :param pig: instance of a pigpio object created by the controller
        :param init_dict: parameters provided at initialization time
                { "ADC": 5, "pin": 1 }
                - ADC: the tb_hardware.id of the ADC (MCP3208) the probe is connected too
                - pin: the ADC's pin
        :param ADC: only for testing - provide the MCP3208 PWO
        """
        self.pig = pig
        self.ADC = ADC #  or self.pig.get_pwo("Hardware", init_dict["ADC"])
        self.pin = init_dict["pin"]
        self.debug = max(debug, init_dict.get("debug", 0))
        if self.debug>=3: print("--->  ADC:", self.ADC)


    def read(self, pin=None, param=5.0):
        """Reads the voltage and convert to pH
            param is the reference voltage
        """
        if self.debug>=3: print("--> Called to read on", self.ADC)
        data, volts12bits = self.ADC.average(self.pin, samples=10, param=param) if self.pig.connected else 1000, 2.0
        if self.debug>=3: print("readings: {}, {}".format(data, volts12bits))
        return data[0], volts12bits * 3.5 # coefficient from documentation

    def __str__(self):
        return "pH Gravity probe on ADC pin {}".format(self.pin)

if __name__ == "__main__":
    import pigpio
    from hardware_MCP3208 import Hardware_MCP3208
    from time import sleep
    pig = pigpio.pi()
    mcp3208 = Hardware_MCP3208(pig, { "channel": 0, "baud": 50000, "flags":0 })
    gravity_pH = Hardware_Gravity_pH(pig, init_dict={ "pin": 1}, ADC=mcp3208, debug=3)
    try:
        while True:
            data, pH = gravity_pH.read()
            print("Read: {} , converted as pH={:.2f}".format(data, pH))
            sleep(2)
    finally:
        mcp3208.cleanup()
