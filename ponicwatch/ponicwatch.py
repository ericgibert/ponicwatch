#!/usr/bin/env python3
"""
    Created by Eric Gibert on 12 May 2016

    Controller
"""
import argparse
import os.path
from croniter import croniter
from datetime import datetime
from time import sleep
from model.pw_db import Ponicwatch_db
from model.pw_log import Ponicwatch_log
from model.user import User
from model.sensor import Sensor as db_sensor

# specific hardware
from drivers.hardware_dht import Hardware_DHT
from drivers.sensor_dht import Sensor_DHT

DEBUG = True  # activate theDebug mode or not

class Controller(object):

    def __init__(self, db):
        self.db = db
        # finding the Controller User entry
        self.user = User(self.db, "ctrl", "passwd")
        self.name = self.user["name"]
        # opening the LOG
        self.log = Ponicwatch_log(self.db, debug=DEBUG)
        self.log["controller_name"] = self.name

        # create the sensors and their supporting hardware as a dictionary
        #   - key: hardware chip
        #   - value: (hardware driver, list of sensors object containing associated tothe harware)
        self.sensors = {}
        now = datetime.now()
        for sensor in db_sensor.list_sensors(self.db):
            # split the 'hardware' text field in its components
            hw_components = sensor["hardware"].split('.')
            hw_id = hw_components[0] + '.' + hw_components[1]
            new_sensor = None
            if hw_id in self.sensors: # if the hardware has been already defined --> just add the new sensor to its list
                (_h, _l) = self.sensors[hw_id]
                if hw_components[0] in ["DHT11", "DHT22", "AM2302"]:
                    new_sensor = Sensor_DHT(_h, sensor)
                    _l.append(new_sensor)
            else: # a new hardware needs to be created then that sensor starts its list
                if hw_components[0] in ["DHT11", "DHT22", "AM2302"]:
                    assert(len(hw_components) == 3)
                    hw_dht = Hardware_DHT(hw_components[0], hw_components[1])  # model and pin number foe the deriver
                    new_sensor = Sensor_DHT(hw_dht, sensor)
                    self.sensors[hw_id] = ( hw_dht,[ new_sensor ])  # store the hardware object and a singleton sensor
                else:
                    print("ERROR: unknown hardware in sensor table:", hw_components[0])
                    print(sensor)

            # when do we need to read the sensor?
            if new_sensor:
                new_sensor.cron = croniter(sensor["timer"], now)
                new_sensor.next_read = new_sensor.cron.get_next(datetime).strftime("%Y-%m-%d %H:%M")
                if DEBUG:
                    print(new_sensor.name, "next read at:", new_sensor.next_read)
        # print(self.sensors)


    def run(self):
        self.log.add_info("Controller is now running")
        self.running = True

        while self.running:
            now = datetime.now().strftime("%Y-%m-%d %H:%M")  # should we take local time or UTC?
            for hw, sensor_list in self.sensors.values():
                # is there a sensor that needs to be read now?
                for sensor in sensor_list:
                    if sensor.next_read == now:
                        hw.read()
                        break
                # ok, let's get the sensors reading from their hardware and set them for their next reading time
                for sensor in sensor_list:
                    if sensor.next_read == now:
                        sensor.calculate_value()
                        print(sensor.name, sensor.calculated_value)
                        sensor.db_rec["calculated_value"] = sensor.calculated_value
                        self.log.add_log(self.name, system_name="Horizon 1", param=sensor.db_rec)
                        sensor.next_read = sensor.cron.get_next(datetime).strftime("%Y-%m-%d %H:%M")
                        if DEBUG:
                            print(sensor.name, "next read at:", sensor.next_read)

            while now == datetime.now().strftime("%Y-%m-%d %H:%M"):
                sleep(10)





def exist_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.isfile(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sqlite", dest="dbfilename",  # type=exist_file, # required=False,
                        help="Path of a Sqlite3 database.")
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()

    if args.dbfilename:
        db = Ponicwatch_db("sqlite3", [args.dbfilename])
        ctrl = Controller(db)
        ctrl.run()
    else:
        print("currently: -s dbfilename is mandatory")
