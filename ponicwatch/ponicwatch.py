#!/usr/bin/env python3
"""
    Created by Eric Gibert on 12 May 2016

    Controller
"""
import argparse
import os.path
from datetime import datetime
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

        # create the sensors and their supporting hardware
        self.sensors = {}  # key: hardware chip, values: sensors object containing the values
        for sensor in db_sensor.list_sensors(self.db):
            # split hardware in components
            hw_components = sensor["hardware"].split('.')
            if hw_components[0] in ["DHT11", "DHT22", "AM2302"]:
                assert(len(hw_components) == 3)
                hw_dht = Hardware_DHT(hw_components[0], hw_components[1])  # model and pin number
                sensor_dht = Sensor_DHT(hw_dht, sensor)
                hw_id = hw_components[0] + '.' + hw_components[1]
                if hw_id in self.sensors:
                    h, l = self.sensors[hw_id]
                    l.append(sensor_dht)
                else:
                    self.sensors[hw_id] = ( hw_dht,[ sensor_dht ])  # the hardware object and a list of sensors
            else:
                print("ERROR: unknown hardware in sensor table:", hw_components[0])
                print(sensor)
        print(self.sensors)


    def run(self):
        self.log.add_info("Controller is now running")
        self.running = True

        for hw, sensor_list in self.sensors.values():
            hw.read()
            print("read HW", hw.temperature, hw.humidity)

            for sensor in sensor_list:
                print(sensor.name, sensor.calculated_value)

        # while self.running:
        #     now = datetime.now()  # should we take local time or UTC?





def exist_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.isfile(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sqlite", dest="dbfilename",  type=exist_file, # required=False,
                        help="Path of a Sqlite3 database.")
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()

    if args.dbfilename:
        db = Ponicwatch_db("sqlite3", [args.dbfilename])
        ctrl = Controller(db)
        ctrl.run()
    else:
        print("currently: -s dbfilename is mandatory")
