#!/bin/python3
"""
    Model for the table tb_sensor.
    Created by Eric Gibert on 29 Apr 2016

    Sensors are objects linked to a hardware pin (on/off digital input) or an analog input to capture a sensor's state.
    They belong to one Controller.
"""
from datetime import datetime, timezone
from model.model import Ponicwatch_Table

class Sensor(Ponicwatch_Table):
    """
    - 'sensor_id' and 'name' identify uniquely a sensor within a Controller database.
    - 'mode': analog or digital
    - 'hardware': identification of the hardware underlying the sensor. Usually a pin number within an IC.
        * RPI3.4: GPIO 4 of the RPI3 --> declare it as 'Analog Input' to read 0/1 for on/off
        * AM2302.4.T and AM2302.4.H --> IC to read both temperature and humidity, hence the need to add extra 3rd param
        * MCP3208.4 --> reads the voltage on the chip's Channel 4
        * MCP23017/MCP23S17.4 --> analog input on channel 4 of the I/O Expander
        * DS18B20.4 --> read temperature given by the DS18B20 probe on pin 4
    - 'read_value': last reading, always as float even for digital input. Float between 0.0 and 1.0 to be converted.
    - 'calculated_value': conversion of the 'read_value' to reflect the expected metric
    Note: if the physical sensor already provides a converted value then 'read_value' = 'calculated_value'
    """
    MODE = {
        0: "DIGITIAL",    # sensor mode is digital 0/1 i.e. pin input reflecting a ON/OFF or True/False i.e. contactor
        1: "ANALOG",      # sensor is connected to an ADC reading the current of a probe. Float between 0.0 and 1.0 to be converted.
        2: "DIRECT",      # sensor provides a direct reading of the true value i.e. usually specific IC connected by i2c or 1-wire protocols
    }

    META = {"table": "tb_sensor",
            "id": "sensor_id",
            "columns": (
                          "sensor_id",          # INTEGER NOT NULL,
                          "name",               # TEXT NOT NULL,
                          "mode",               # INTEGER NOT NULL DEFAULT (0),
                          "hardware",           # TEXT NOT NULL,
                          "timer",              # TEXT,
                          "read_value",         # FLOAT NOT NULL DEFAULT (0.0),
                          "calculated_value",   # REAL NOT NULL DEFAULT (0.0)
                          "timestamp_value",    # TIMESTAMP,
                          "updated_on",         # TIMESTAMP,
                          "synchro_on",         # TIMESTAMP
                        )
            }

    def __init__(self, controller, system_name, hardware, *args, **kwargs):
        super().__init__(controller.db, Sensor.META, *args, **kwargs)
        self.controller = controller
        self.hardware = hardware
        if hardware["mode"] == 2:  # R/W
            self.hardware.set_pin_as_input(self.pins)
        self.system_name = system_name + "/" + self["name"]
        self.controller.add_cron_job(self.execute, self["timer"])

    def get_record(self, id=None, name=None):
        """
        Fetch one record from tb_sensor matching either of the given parameters
        :param name: tb_sensor.name (string)
        :param id: tb_sensor.sensor_id (int)
        """
        super().get_record(id, name)
        hw_parts = self["hardware"].split('.')  # example:"AM2302.4.T" --> ['AM2302', '4', 'T']
        self.IC, self.pins, self.hw_param = hw_parts[0], hw_parts[1], hw_parts[2] if len(hw_parts) == 3 else None

    def execute(self):
        """Called by the scheduler to perform the data reading"""
        read_val, calc_val = self.hardware.read(self.pins, self.hw_param)
        if read_val is None:
            self.controller.log.add_error("Cannot read from " + str(self), self["id"])
        else:
            self.update_values(read_val, calc_val)
            self.controller.log.add_log(system_name=self.system_name, param=self)

    def update_values(self, read_value, calculated_value):
        self.update(read_value=read_value,
                    calculated_value=calculated_value,
                    updated_on=datetime.now(timezone.utc))

    @classmethod
    def all_keys(cls, db):
        return super().all_keys(db, Sensor.META)

    def __str__(self):
        return "{} ({})".format(self["name"], Sensor.MODE[self["mode"]])


if __name__ == "__main__":
    from model.pw_db import Ponicwatch_Db
    pw_db = Ponicwatch_Db("sqlite3", {"database": "ponicwatch.db"})

    print(Sensor.all_keys(pw_db))

    sensor1 = Sensor(pw_db, sensor_id=1)
    print(sensor1)
