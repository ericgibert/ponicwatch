#!/bin/python3
"""
    Model for the table tb_sensor.

    Sensors are objects linked to a hardware pin (on/off digital input) or an analog input to capture a sensor's state.
    They belong to one Controller.

    - 'sensor_id' and 'name' identify uniquely a sensor within a Controller database.
    - 'mode': analog or digital
    - 'hardware': identification of the hardware undelying the sensor. Usually a pin number within an IC.
    - 'read_value': last reading, always as float even for digital input. Float between 0.0 and 1.0 to be converted.
    - 'calculated_value': conversion of the 'read_value' to reflect the expected metric
    Note: if the peripheric already provides a converted value then 'read_value' = 'calculated_value'
"""

class Sensor(object):
    """

    """
    DIGITIAL = 0    # sensor mode is digital 0/1 i.e. pin input reflecting a ON/OFF or True/False i.e. contactor
    ANALOG = 1      # sensor is connected to an ADC reading the current of a probe. Float between 0.0 and 1.0 to be converted.
    DIRECT = 2      # sensor provides a direct reading of the true value i.e. usually specific IC connected by i2c or 1-wire protocols

    def __init__(self, db, name=None, id=None):
        self.db = db
        (self.sensor_id, self.name, self.mode, self.hardware,
         self.read_value, self.calculated_value) = None, None, None, None, None, None
        if name:
            self.get_sensor(name=name)
        elif id:
            self.get_sensor(id=id)

    def get_sensor(self, name=None, id=None):
        """
        Fetch one record from tb_sensor matching either of the given parameters
        :param name: tb_sensor.name (string)
        :param id: tb_sensor.sensor_id (int)
        """
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                if name and type(name) is str:
                    curs.execute("SELECT * from tb_sensor where name=?", (name,))
                elif id and type(id) is int:
                    curs.execute("SELECT * from tb_sensor where sensor_id=?", (id,))
                else:
                    raise ValueError
                sensor_row = curs.fetchall()
                if len(sensor_row) == 1:
                    (self.sensor_id, self.name, self.mode, self.hardware,
                     self.read_value, self.calculated_value) = sensor_row[0]
            finally:
                curs.close()

    def __str__(self):
        return "{} ({})".format(self.name, self.mode)