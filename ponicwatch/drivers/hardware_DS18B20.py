"""
    DS18B20 Temperature Sensing - used for reading water temperature
    Measure temperature with your Raspberry Pi using the DS18B20

    reference: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware
"""
import os
from time import sleep
from glob import glob
from random import randint
try:
    from pigpio import FILE_READ, error as pig_error
except ImportError:
    FILE_READ = 1
    pig_error = ValueError

class Hardware_DS18B20(object):
    """
    Identify and read data from a DS18B20 temperature probe
    """
    base_dir = '/sys/bus/w1/devices/'

    @classmethod
    def list_probes(cls):
        """List all probes found"""
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        return glob(cls.base_dir + '28*')

    def __init__(self, pig, device_folder, debug=0):
        self.pig = pig
        self.device_file = device_folder + '/w1_slave'
        self.debug = debug
        if os.path.isfile(self.device_file):
            self.simulation = False
        elif self.pig.connected:
            self.simulation = False
            if self.debug>=3: print("Remote read of", self.device_file)
        else:
            self.simulation = True
            print("Simulation on", self)
        self.temperature = 0.0  # only the Celcius is kept (F is ignored)

    def __str__(self):
        return "Probe DS18B20 on {}".format(self.device_file)

    def read_temp_raw(self):
        """
        A file may only be opened if permission is granted by an entry in
      /opt/pigpio/access.  This is intended to allow remote access to files
      in a more or less controlled manner.

      Each entry in /opt/pigpio/access takes the form of a file path
      which may contain wildcards followed by a single letter permission.
      The permission may be R for read, W for write, U for read/write,
      and N for no access.


      /sys/bus/w1/devices/* r


        :return:
        """
        if os.path.isfile(self.device_file):
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
                return lines
        else:
            try:
                h = self.pig.file_open(self.device_file, FILE_READ)
                c, data = self.pig.file_read(h, 1000)  # 1000 is plenty to read full file.
                self.pig.file_close(h)
            except pig_error:
                data = b"xxxxxxxxxxxxxxxxxx\nxxxxxxxxxxxxxxxx\nxxxxxxxxxxxxx"
            return data.decode("utf-8").split('\n')

    def read(self, pin=None, param=None):
        """Get the temperature.
        Both params are ignored as the information is provided at __init__ time
        """
        if self.simulation:
            self.temperature = randint(25, 35)
        else:
            self.temperature = None
            lines = self.read_temp_raw()
            # print(lines)
            tries = 10
            while lines[0].strip()[-3:] != 'YES' and tries > 0:
                sleep(0.2)
                lines = self.read_temp_raw()
                tries -= 1
            if tries > 0:
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_string = lines[1][equals_pos + 2:]
                    temp_c = float(temp_string) / 1000.0
                    # temp_f = temp_c * 9.0 / 5.0 + 32.0
                    self.temperature = temp_c if temp_c < 85.0 else None
        return (self.temperature, self.temperature)


if __name__ == "__main__":
    import time
    import pigpio
    pi = pigpio.pi()
    probes = []
    list_of_files = Hardware_DS18B20.list_probes()
    print(list_of_files)
    for probe_folder in list_of_files:
        probes.append(Hardware_DS18B20(pi, probe_folder, debug=3))

    if probes:
        while True:
            for probe in probes:
                probe.read()
                print(probe, probe.temperature)
            time.sleep(1)
    else:
        print("No probe detected - Abort -")
