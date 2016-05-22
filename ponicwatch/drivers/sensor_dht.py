#/bin/python3
"""
    Create a sensor based on the IC DHT11, DHT22 or AM3202
    This IC can read ambiant temperature and humidity
"""
from drivers.sensor import Sensor

class Sensor_DHT(Sensor):
    """
        Only expects a GPI pin for dialog
    """
    def __init__(self, hw_dht, sensor_db_rec):
        """
        :param sensor_def: object retrieved from the database to create this sensor instance
        """
        print(sensor_db_rec["name"])
        super().__init__(sensor_db_rec["name"])
        self. hw = hw_dht
        # expected string for hardware: [DHT11|DHT22|AM2302].<pin>.[T: temperature|H:humidity]
        # example:  AM2302.4.T  : reads the temperature on an AM2302 connected on pin GPIO 4
        hdware = sensor_db_rec["hardware"].split('.')
        assert(len(hdware) == 3)
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

