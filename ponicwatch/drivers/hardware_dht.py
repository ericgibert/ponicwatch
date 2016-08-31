#/bin/python3
"""
    Manage the IC DHT11, DHT22 or AM3202
    This IC can read ambiant temperature and humidity
"""
# refer to https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated
# source at: git clone https://github.com/adafruit/Adafruit_Python_DHT.git
try:
    import Adafruit_DHT
except ImportError:
    from random import randint
    class Adafruit_DHT():
        @staticmethod
        def read_retry(model, pin):
            print("DHT simulation")
            return (randint(50, 80), randint(25, 35))

class Hardware_DHT(object):
    """
        Only expects a GPI pin for dialog
    """
    def __init__(self, model, pin):
        """
        :param model: DHT11|DHT22|AM2302
        :param pin: the data pin of the IC
        """
        self.model, self.pin = (11 if model=='DHT11' else 22), int(pin)
        self.temperature = -100.0
        self.humidity = -100.0

    def read(self, T_or_H):
        """
        Reads the values from the IC
        The temprature MUST be called first as it will perform the actual read
        """
        if T_or_H == "T":
            humidity, temperature = Adafruit_DHT.read_retry(self.model, self.pin)
            if humidity is not None and temperature is not None:
                self.humidity, self.temperature = humidity, temperature
            return (self.temperature, self.temperature)
        else:
            return (self.humidity, self.humidity)

