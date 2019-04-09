#!/bin/env python
"""
    Manage the IC DHT11, DHT22 or AM3202
    This IC can read ambient temperature and humidity

    Wrapper around the DHT22.py driver provided below:

    refer to https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/software-install-updated
    source at: git clone https://github.com/adafruit/Adafruit_Python_DHT.git
"""
from datetime import datetime
from time import sleep
from random import randint
try:
    from drivers.DHT22 import dht_sensor
except ImportError:
    print("Simulation for DHT22")


class dht_sensor_simu():
    def __init__(self, pig, pin):
        pass
    def read_retry(self, model, pin):
        print("DHT simulation")
        self.trigger()
        return (self._humidity, self._temperature)
    def humidity(self): return self._humidity
    def temperature(self): return self._temperature
    def trigger(self):
        self._humidity, self._temperature = randint(50, 80), randint(25, 35)

class Hardware_DHT(object):
    """
        Only expects a GPI pin for dialog
    """
    supported_models = ("DHT11", "DHT22", "AM2302")
    def __init__(self, pig, model, pin, debug=0):
        """
        :param pig: instance of a pigpio object created by the controller
        :param model: DHT11|DHT22|AM2302
        :param pin: the IC data pin on the Raspberry Pi
        """
        self.model, self.pin = (11 if model=='DHT11' else 22), pin
        self.temperature = None
        self.humidity = None
        self.last_read = datetime.now()
        self.sensor = dht_sensor(pig, self.pin) if pig.connected else dht_sensor_simu(pig, self.pin)
        self.debug = debug
      
    def read(self, pins, T_or_H):
        """
        Reads the values from the IC
        3 seconds gap is guarantied between 2 readings
        Note: param pins is ignored as the reading pin is defined at __init__ time already
        """
        if self.debug>=3: print("T_or_H:", T_or_H)
        if (datetime.now() - self.last_read).seconds > 3 or self.humidity is None:
            #humidity, temperature = Adafruit_DHT.read_retry(self.model, self.pin)
            self.sensor.trigger()
            sleep(0.2)
            humidity, temperature = self.sensor.humidity(), self.sensor.temperature()
            if self.debug >= 3: print("humidity, temperature =", (humidity, temperature))
            if humidity is not None and temperature is not None:
                self.humidity, self.temperature = humidity, temperature
                self.last_read = datetime.now()
        return (self.temperature, self.temperature) if T_or_H == "T" else (self.humidity, self.humidity)

    def write(self):
        raise NotImplementedError("Air temperature and humidity sensor: read only IC i.e. cannot write")


if __name__ == "__main__":
    import sys
    import pigpio

    if len(sys.argv) != 2:
        print("Usage: hardware_DHT.py <pin_number>")
        exit(1)

    pig = pigpio.pi("127.0.0.1", 8888)
    pig.connected = True
    pin = int(sys.argv[1])
    print(pin)
    dht = Hardware_DHT(pig, "AM2302", pin, debug=3)
    print("Temperature:", dht.read(T_or_H='T'))
    print("Humidity:", dht.read(T_or_H='H'))

