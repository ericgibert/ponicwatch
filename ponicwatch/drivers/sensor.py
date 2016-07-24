#/bin/python3
"""
    Created by Eric Gibert on 12 May 2016

    Generic class for all Sensors

    Sensors are all form of input:
    - digital
    - analog
    - direct read
"""

class Sensor(object):
    """Interface for all sensors"""
    def __init__(self, name):
        self.read_value = 0.0 # last reading
        self.calculated_value = 0.0  # last calculated value from reading value
        self.name = name

    def calculate_value(self):
        """Surclass to implement an alogrithm to convert a read value into a calculated one - more meaningfull for human"""
        self.calculated_value = self.read_value

    def read(self):
        """Read the sensor"""
        raise NotImplementedError

    def set_controller(self, ctrl):
        """refer to the controller and its logger"""
        self.ctrl = ctrl
        self.logger = ctrl.log

    def __str__(self):
        return "Sensor {}".format(self.name)