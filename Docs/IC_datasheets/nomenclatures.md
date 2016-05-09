DHT22 direct pin
================

https://learn.adafruit.com/downloads/pdf/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging.pdf
Don't forget to connect a 4.7K - 10K resistor from the data pin to VCC (if 4.7K doesn't work, try 10K)

Requieres: 1 GPIO pin. [Connected to any GPIO pin on the Raspi]
DHT22:
- pin 1 (left most): +3.3V = VCC
- pin 2: GPIO = data pin
- pin 3: n/a
- pin 4 (right most): GND


Other links:
http://www.instructables.com/id/Raspberry-PI-and-DHT22-temperature-and-humidity-lo/?ALLSTEPS


DS18B20 "1-wire" sensor
=======================

https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/parts

You need a ~4.7K-10K resistor from data to 3.3V.
- Red: 3.3V = VCC
- Black/Blue: GND
- Yellow/White: data pin 

http://www.raspberrypi-spy.co.uk/2013/03/raspberry-pi-1-wire-digital-thermometer-sensor/

Need to adapt /boot/config.txt
