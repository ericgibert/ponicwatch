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
    read_value = 0.0
    calculated_value = 0.0
    name = ""
    def __init__(self, name):
        # self.read_value = 0.0 # last reading
        # self.calculated_value = 0.0  # last calculated value from reading value
        # self.name = name
        pass

    def calculate_value(self):
        """Surclass to implement an alogrithm to convert a read value into a calculated one - more meaningfull for human"""
        self.calculated_value = self.read_value

    def read(self):
        """Read the sensor"""
        raise NotImplementedError