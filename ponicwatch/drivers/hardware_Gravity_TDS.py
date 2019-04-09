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

    def __init__(self, pig, init_dict, ADC=None, water_temp_sensor=None, debug=0):
        """

        :param pig: instance of a pigpio object created by the controller
        :param init_dict: parameters provided at initialization time
                { "ADC": 5, "pin": 1 , "water_temp_sensor": 3}
                - ADC: tb_hardware.id of the ADC (MCP3208) the probe is connected too
                - pin: the ADC's pin
                - water_temp_sensor: tb_hardware.id of the water temperature sensor
        :param ADC: only for testing - provide the ADC PWO
        :param water_temp_sensor: only for testing - provide the DS18B20 PWO
        """
        self.pig = pig
        self.ADC = ADC #  or self.pig.get_pwo("Hardware", init_dict["ADC"])
        self.pin = init_dict["pin"]
        self.water_temp_sensor = water_temp_sensor or self.pig.get_pwo("Sensor", init_dict["water_temp_sensor"])
        self.debug = max(debug, init_dict.get("debug", 0))
        if self.debug>=3: print("--->  TDS:", self.ADC, self.pin, self.water_temp_sensor)

    def read(self, pin=None, param=5.0):
        """Reads the voltage and convert to pH
            param is the reference voltage
        """
        if self.debug>=3: print("Reading TDS probe...", end="")
        data, volts12bits = self.ADC.average(self.pin, samples=10, param=param) if self.pig.connected else 1000, 0.2
        if self.debug >= 3:
            print(data, volts12bits)
            print("Reading water temperature...", end="")
        temperature = self.water_temp_sensor.value # if self.pig.connected else 21.0
        if self.debug>=3: print(temperature)
        compensationCoefficient = 1.0 + 0.02 * (temperature - 25.0)
        compensationVolatge = volts12bits / compensationCoefficient
        tdsValue = (133.42 * compensationVolatge * compensationVolatge * compensationVolatge
                    - 255.86 * compensationVolatge * compensationVolatge
                    + 857.39 * compensationVolatge) * 5.5  #0.5
        return data[0], round(tdsValue)

if __name__ == "__main__":
    import pigpio
    from hardware_MCP3208 import Hardware_MCP3208
    from hardware_DS18B20 import Hardware_DS18B20
    from time import sleep
    pig = pigpio.pi()
    mcp3208 = Hardware_MCP3208(pig, { "channel": 0, "baud": 50000, "flags":0 })
    list_of_files = Hardware_DS18B20.list_probes()
    print("Found the following probes:", list_of_files)
    ds18b20 = Hardware_DS18B20(pig, list_of_files[0]) if list_of_files else "not_found"  # first probe selected for testing
    gravity_tds = Hardware_Gravity_TDS(pig, init_dict={ "pin": 2}, ADC=mcp3208, water_temp_sensor=ds18b20, debug=3)
    try:
        while True:
            data, ppm = gravity_tds.read(0)
            print("Read: {} , converted as {}ppm".format(data, ppm))
            sleep(2)
    finally:
        mcp3208.cleanup()
