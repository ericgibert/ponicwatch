#!/bin/env python
"""
    Reads the signal provided by the Gravity TDS probe

    https://www.dfrobot.com/product-1662.html

    Requires a ADC to read the voltage from the signal pin
    Conversion follows the algorithm given at:
    https://www.dfrobot.com/wiki/index.php/Gravity:_Analog_TDS_Sensor_/_Meter_For_Arduino_SKU:_SEN0244

    Declaration in the database: tb_hardware.hardware == GRAVITY_TDS
"""


class Hardware_Gravity_TDS(object):
    """
      Connection on +5V and Ground + signal on ADC pin
    """

    def __init__(self, pig, init_dict, MCP3208=None, DS18B20=None):
        """

        :param pig: instance of a pigpio object created by the controller
        :param init_dict: parameters provided at initialization time
                { "MCP3208": 5, "pin": 1 , "temperature": 3}
                - MCP3208: tb_hardware.id of the MCP3208 the probe is connected too
                - pin: the MCP3208's pin
                - temperature: tb_hardware.id of the water temperature sensor
        :param MCP3208: only for testing - provide the MCP3208 PWO
        :param DS18B20: only for testing - provide the DS18B20 PWO
        """
        self.pig = pig
        self.MCP3208 = MCP3208 or self.pig.get_pwo("Hardware", init_dict["MCP3208"])
        self.pin = init_dict["pin"]
        self.water_temp = DS18B20 or self.pig.get_pwo("Sensor", init_dict["temperature"])

    def read(self, pin=None, param=5.0):
        """Reads the voltage and convert to pH
            param is the reference voltage
        """
        data, volts12bits = self.MCP3208.average(channel=self.pin, samples=10, param=param)
        temperature = 23.0 if self.water_temp == "not_found" else self.water_temp.read()
        compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)
        compensationVolatge = volts12bits / compensationCoefficient
        tdsValue = (133.42 * compensationVolatge * compensationVolatge * compensationVolatge
                    - 255.86 * compensationVolatge * compensationVolatge
                    + 857.39 * compensationVolatge) * 0.5
        return data, tdsValue

if __name__ == "__main__":
    import pigpio
    from hardware_MCP3208 import Hardware_MCP3208
    from hardware_DS18B20 import Hardware_DS18B20
    from time import sleep
    pig = pigpio.pi()
    mcp3208 = Hardware_MCP3208(pig, { "channel": 0, "baud": 50000, "flags":0 })
    list_of_files = Hardware_DS18B20.list_probes()
    ds18b20 = Hardware_DS18B20(pig, list_of_files[0]) if list_of_files else "not_found"  # first probe selected for testing
    gravity_tds = Hardware_Gravity_TDS(pig, init_dict={ "pin": 0}, MCP3208=mcp3208, DS18B20=ds18b20)
    try:
        while True:
            data, ppm = gravity_tds.read(0)
            print("Read: {} , converted as {}ppm".format(data, round(ppm)))
            sleep(2)
    finally:
        mcp3208.cleanup()