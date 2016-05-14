#/bin/python3
"""
    Create a sensor based on the IC AM3202 (same as DHT22)
"""
from sensor import Sensor
import Adafruit_DHT     # refer to https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated
                        # source at: git clone https://github.com/adafruit/Adafruit_Python_DHT.git

class AM3202(Sensor):
    """
        Only expects a GPI pin for dialog
    """
    def __init__(self, sensor_def):
        """

        :param sensor_def: object retrieved from the database to create this sensor instance
        """
        Sensor.__init__(sensor_def["name"])
        # expected string for hardware: [DHT11|DHT22|AM2302].<pin>.[T: temperature|H:humidity]
        # example:  AM2302.4.T  : reads the temperature on an AM2302 connected on pin GPIO 4
        hdware = sensor_def["hardware"].split('.')
        assert(len(hdware), 3)
        self.IC, self.pin, self.mode = hdware[0], int(hdware[1]), hdware[2]
        self.temperature = 0
        self.humidity = 0

    def read(self):
        """

        :return:
        """
        humidity, temperature = Adafruit_DHT.read_retry(self.IC, self.pin)
        if humidity is not None and temperature is not None:
            self.humidity, self.temperature = humidity, temperature

    @property
    def calculated_value(self):
        """
        Accordingly to the Sensor mode (T or H)
        Note: read_value and calculated_value are the same
        :return: temperature or humidity
        """
        return self.temperature if self.mode == 'T' else self.humidity

    @property
    def read_value(self):
        """
        Accordingly to the Sensor mode (T or H)
        Note: read_value and calculated_value are the same
        :return: temperature or humidity
        """
        return self.temperature if self.mode == 'T' else self.humidity
