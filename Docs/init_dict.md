Description of all possible entries in PWO's init dictionary
============================================================

The following PonicWatch Objects have a 'init' column in their table:
- Hardware
- Interrupt
- Sensor
- Switch

The field is of type 'TEXT NOT NULL' and contains a JSON string.

Ponicwatch_Table
----------------
During the creation of a PWO, the function 'get_record' provides:

    self.init_dict = json.loads(self["init"])

This ensures the the PWO has its init dictionary initialized.    

Hardware
--------

|Key    |Type   |Definition or Usage                            |Used on|
|-------|-------|-----------------------------------------------|-------|
|pin    |int    |Indicates which RPI3's pin is used by an IC    |       |
|path   |str    |provides the path to one w1 sensor             |DS18B20|
|IN     |[int]  |list on pins to set as INPUT                   |RPI3   |
|OUT    |[int]  |list on pins to set as OUTPUT                  |RPI3   |
|INTER  |[int]  |list on pins to link to interruption           |RPI3   |
|bus    |int    |i2c protocol: 1 for RPI3                       |MCP23017|
|address|int or str(int)|i2c protocol: decinal or hexadecimal address of the IC|MCP23017|
|interrupt|tbd  | not yet sure how to handle interruptions      |MCP23017|
|ON_value|0 or 1|define the  value to use to set a pin to ON    |MCP23017|
|names  |dict   |dictionary to give each pin a name for display |MCP23017|
|channel|int    |SPI protocol                                   |MCP3208 |
|baud   |int    |SPI protocol                                   |MCP3208 |
|flags  |int    |SPI protocol                                   |MCP3208 |



Interrupt
---------

|Key    |Type   |Definition or Usage                            |Used on|
|-------|-------|-----------------------------------------------|-------|
|action |function|callback function texecuted when interruption occurs| |
|timer  |cron time|define the interruption as a timer           |       |



Sensor
------

|Key    |Type   |Definition or Usage                            |Used on|
|-------|-------|-----------------------------------------------|-------|
|IC     |str    |name of the hardware used by the sensor        |       |
|pin    |int    |pin for reading the measuere reported by the sensor on the nammed hardware|        |
|hw_param|str/free|optional: parameters for the hardware driver |       |
|LOG	|ON	| Default: LOG insert happens a each reading execution
|LOG	|OFF	| Does NOT INSERT in tb_log after reading execution
|LOG	|DIFF	| Insert in LOG after reading execution ONLY if new read value is different from last




Switch
------

|Key    |Type   |Definition or Usage                            |Used on|
|-------|-------|-----------------------------------------------|-------|
|IC     |str    |name of the hardware used by the sensor        |       |
|pin    |int    |pin for reading the measuere reported by the sensor on the nammed hardware|        |
|set_value_to|0 or 1|set the swicth to this value at timed execution|       |
|if     |str    |condition to fill for the switch execution     |       |
|if     |[str]  |list of strings: first is the format then the arguments   |        |
