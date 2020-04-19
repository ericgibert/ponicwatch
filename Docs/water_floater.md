Water Floater
=============


Two floaters: top and bottom

* Black cables for switch on bottom floater
* Red cables for swtich on top floater


Circuit
-------

+5V
 |
 ----  floater cable
 ----
 |
 --------  Pin Input Bx of MCP2307
 |
 -------- long leg LED
 -------- short leg LED
 |
( )     Resistance not too strong
 |
 =     GND


Usage
-----

In tb_sensor:
	init: {"IC":"MCP23017","pin":"B0","comment":"Black cables for bottom"}
	or
	init: {"IC":"MCP23017","pin":"B1","comment":"Red cables for top"}

In tb_link:
	add entry between these sensors and the hardware ID for MCP2307

Reminder: reading every minutes on the 10 sec.: 10 * * * * *



