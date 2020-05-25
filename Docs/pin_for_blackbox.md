
Tent Humidity and Temperature Captor
	AM2302	{ "pin": 17}
	
Air Humidity and Temperature Captor
    AM2302	{ "pin": 18}
	
Water Temperature
	DS18B20	{ "path": "/sys/bus/w1/devices/28-021581795fff" }
    Pin #4 on RPI3
    
16 I/O MCP23107	
    { "bus":1, "address": "0x20", "interrupt": "", "names":{"A0": "Spray Pump", "A1": "Fans", "A2": "Water Resist", "A3": "Light", "A4": "Air Heater"}}	

A0-A4 for 220V switches
    A0-A3: 4 solid switches
    A4: special extra for plug M