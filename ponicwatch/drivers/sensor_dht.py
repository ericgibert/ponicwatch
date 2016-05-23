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
        # print(sensor_db_rec["name"])
        Sensor.__init__(self, sensor_db_rec["name"])
        self. hw = hw_dht
        self.db_rec = sensor_db_rec
        # expected string for hardware: [DHT11|DHT22|AM2302].<pin>.[T: temperature|H:humidity]
        # example:  AM2302.4.T  : reads the temperature on an AM2302 connected on pin GPIO 4
        hdware = sensor_db_rec["hardware"].split('.')
        assert(len(hdware) == 3)
        self.IC, self.pin, self.mode = hdware[0], int(hdware[1]), hdware[2]
        # print(self.mode)

    def calculate_value(self):
        """Assign temperature or humidity read on IC to values"""
        self.calculated_value = self.read_value = (self.hw.temperature if self.mode == 'T' else self.hw.humidity)
        self.db_rec.update_values(self.read_value , self.calculated_value)
        # print(".calculate_value():", self.calculated_value , self.read_value)

