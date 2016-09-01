# reference: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/hardware
import os
from glob import glob



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

    def __init__(self, device_folder):
        self.device_file = device_folder + '/w1_slave'
        self.temperature = 0.0  # only the Celcius is kept (F is ignored)

    def __str__(self):
        return "Probe DS18B20 on {}".format(self.device_file)

    def read_temp_raw(self):
        with open(self.device_file, 'r') as f:
            lines = f.readlines()
        return lines

    def read(self, param=None):
        self.temperature = None
        lines = self.read_temp_raw()
        tries = 10
        while lines[0].strip()[-3:] != 'YES' and tries > 0:
            time.sleep(0.2)
            lines = self.read_temp_raw()
            tries -= 1
        if tries > 0:
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                temp_c = float(temp_string) / 1000.0
                # temp_f = temp_c * 9.0 / 5.0 + 32.0
                self.temperature = temp_c
        return (self.temperature, self.temperature)


if __name__ == "__main__":
    import time
    probes = []
    for probe_folder in Hardware_DS18B20.list_probes():
        probes.append(Hardware_DS18B20(probe_folder))

    if probes:
        while True:
            for probe in probes:
                probe.read()
                print(probe, probe.temperature)
            time.sleep(1)
    else:
        print("No probe detected - Abort -")