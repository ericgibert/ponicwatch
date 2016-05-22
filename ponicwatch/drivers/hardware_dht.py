#/bin/python3
"""
    Manage the IC DHT11, DHT22 or AM3202
    This IC can read ambiant temperature and humidity
"""
# refer to https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated
# source at: git clone https://github.com/adafruit/Adafruit_Python_DHT.git
import Adafruit_DHT

class Hardware_DHT(object):
    """
        Only expects a GPI pin for dialog
    """
    def __init__(self, model, pin):
        """
        :param model: DHT11|DHT22|AM2302
        :param pin: the data pin of the IC
        """
        self.model, self.pin = model[2:], pin
        self.temperature = 0.0
        self.humidity = 0.0

    def read(self):
        """
        Reads the values from the IC
        """
        humidity, temperature = Adafruit_DHT.read_retry(self.model, self.pin)
        if humidity is not None and temperature is not None:
            self.humidity, self.temperature = humidity, temperature

