#/bin/python3
"""
    Create a sensor based on the IC DHT11, DHT22 or AM3202
    This IC can read ambiant temperature and humidity
"""
from drivers.sensor import Sensor
# refer to https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated
# source at: git clone https://github.com/adafruit/Adafruit_Python_DHT.git
import Adafruit_DHT

class Sensor_DHT(Sensor):
    """
        Only expects a GPI pin for dialog
    """
    def __init__(self, hw_dht, sensor_def):
        """
        :param sensor_def: object retrieved from the database to create this sensor instance
        """
        Sensor.__init__(sensor_def["name"])
        self. hw = hw_dht
        # expected string for hardware: [DHT11|DHT22|AM2302].<pin>.[T: temperature|H:humidity]
        # example:  AM2302.4.T  : reads the temperature on an AM2302 connected on pin GPIO 4
        hdware = sensor_def["hardware"].split('.')
        assert(len(hdware), 3)
        self.IC, self.pin, self.mode = hdware[0], int(hdware[1]), hdware[2]


    @property
    def calculated_value(self):
        """
        Accordingly to the Sensor mode (T or H)
        Note: read_value and calculated_value are the same
        :return: temperature or humidity
        """
        return self.hw.temperature if self.mode == 'T' else self.hw.humidity

    @property
    def read_value(self):
        """
        Accordingly to the Sensor mode (T or H)
        Note: read_value and calculated_value are the same
        :return: temperature or humidity
        """
        return self.hw.temperature if self.mode == 'T' else self.hw.humidity
