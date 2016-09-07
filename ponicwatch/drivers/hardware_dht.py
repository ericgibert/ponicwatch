#/bin/python3
"""
    Manage the IC DHT11, DHT22 or AM3202
    This IC can read ambiant temperature and humidity
"""
# refer to https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated
# source at: git clone https://github.com/adafruit/Adafruit_Python_DHT.git
from datetime import datetime
from time import sleep

try:
    import pigpio
    from drivers.DHT22 import sensor
##try:
##    import Adafruit_DHT
except ImportError:
    from random import randint
    print("Simulation for DHT22")
#    class Adafruit_DHT():
    class sensor(*args):
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
        self.temperature = None
        self.humidity = None
        self.last_read = datetime.now()
        self.sensor = sensor(pigpio.pi(), 4)
      

    def read(self, T_or_H):
        """
        Reads the values from the IC
        3 seconds gap is guarantied between 2 readings
        """
        print("T_or_H:", T_or_H)
        if (datetime.now() - self.last_read).seconds > 3 or self.humidity is None:
            #humidity, temperature = Adafruit_DHT.read_retry(self.model, self.pin)
            self.sensor.trigger()
            sleep(0.2)
            humidity, temperature = self.sensor.humidity(), self.sensor.temperature()
            if humidity is not None and temperature is not None:
                self.humidity, self.temperature = humidity, temperature
                self.last_read = datetime.now()
        return (self.temperature, self.temperature) if T_or_H == "T" else (self.humidity, self.humidity)
