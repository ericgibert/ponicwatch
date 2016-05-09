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


MCP3208 ADC with SPI communication
==================================

Graphics
- http://www.paulschow.com/2013/08/monitoring-temperatures-using-raspberry.html
- http://pi.gids.nl:81/adc/
- http://www.arduitronics.com/article/raspberry-pi-analog-input-with-adc-mcp3208

https://www.hackster.io/4796/temperature-sensor-sample-393755

MCP3208: VDD - 5V on RaspBerry Pi2
MCP3208: VREF - 5V on RaspBerry Pi2
MCP3208: CLK - “SPI0 SCLK” on RaspBerry Pi2
MCP3208: Dout - “SPI0 MISO” on RaspBerry Pi2
MCP3208: Din - “SPI0 MOSI” on RaspBerry Pi2
MCP3208: CS/SHDN - “SPIO CS0 on RaspBerry Pi2
MCP3208: DGND - GND on RaspBerry Pi2

Code: https://gist.github.com/yoggy/7096133

or WiringPi: https://projects.drogon.net/raspberry-pi/wiringpi/
for python: https://github.com/WiringPi/WiringPi-Python




LSL100 to ADC
=============

http://www.makenation.co.uk/shop/lsl100-light-sensor/#howtoo
Needs a 1K resistance

VCC -> 1K resistance -> * -> LSL100 -> GND
* Take input to ADC pin between resistance and LSL100.

