#!/usr/bin/env python3
"""
    Created by Eric Gibert on 12 May 2016

    Controller
"""
import argparse
import os.path
from apscheduler.schedulers.background import BackgroundScheduler
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
    """The Controller in a MVC model"""

    def __init__(self, db):
        # keep a link to the database i.e. M in MVC
        self.db = db
        # finding the Controller User entry --> currently 'hard coded' as 'ctrl'/'passwd' --> to improve later
        self.user = User(self.db, "ctrl", "passwd")
        self.name = self.user["name"]  # this name is used to identfy the log messages posted by this controller

        # opening the LOGger with the debug level for this application run
        self.log = Ponicwatch_log(self.db, debug=DEBUG)
        self.log["controller_name"] = self.name  # set as default for controller's log entries

        # Create the background scheduler that will execute the actions
        self.scheduler = BackgroundScheduler()


        # create the sensors and their supporting hardware as a dictionary
        #   - key: hardware chip
        #   - value: tuple (hardware driver, list of sensors object containing associated to the harware)
        self.sensors = {}
        for sensor_rec in db_sensor.list_sensors(self.db):
            new_sensor = None
            if sensor_rec.hw_id in self.sensors: # if the hardware has been already defined --> just add the new sensor to its list
                (_h, _l) = self.sensors[sensor_rec.hw_id]
                if sensor_rec.IC in ["DHT11", "DHT22", "AM2302"]:
                    new_sensor = Sensor_DHT(_h, sensor_rec)
                    _l.append(new_sensor)
            else: # a new hardware needs to be created then that sensor starts its list
                if sensor_rec.IC  in ["DHT11", "DHT22", "AM2302"]:
                    assert(len(sensor_rec.hw_components) == 3)
                    hw_dht = Hardware_DHT(sensor_rec.IC, sensor_rec.pins)  # model and pin number for the driver
                    new_sensor = Sensor_DHT(hw_dht, sensor_rec)
                    self.sensors[sensor_rec.hw_id] = ( hw_dht,[ new_sensor ])  # store the hardware object and a singleton sensor
                else:
                    print("ERROR: unknown hardware in sensor table:", sensor_rec.hw_id)
                    print(sensor_rec)

            # When do we need to read the sensor?
            # ┌───────────── min (0 - 59)
            # │ ┌────────────── hour (0 - 23)
            # │ │ ┌─────────────── day of month (1 - 31)
            # │ │ │ ┌──────────────── month (1 - 12)
            # │ │ │ │ ┌───────────────── day of week (0 - 6) (0 to 6 are Sunday to
            # │ │ │ │ │                  Saturday, or use names; 7 is also Sunday)
            # │ │ │ │ │
            # │ │ │ │ │
            # * * * * *
            if new_sensor:
                new_sensor.set_controller(self)
                min, hrs, dom, mon, dow = sensor_rec["timer"].split()  # like "*/5 * * * *" --> every 5 minutes
                self.scheduler.add_job(new_sensor.read, 'cron', second=min, hour=hrs, day=dom, month=mon, day_of_week=dow)
        # print(self.sensors)


    def run(self):
        """Starts the APScheduler task"""
        self.running = True
        self.scheduler.start()
        self.log.add_info("Controller is now running")
        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while self.running :
                sleep(2)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            self.scheduler.shutdown()


        # while self.running:
        #     now = datetime.now().strftime("%Y-%m-%d %H:%M")  # should we take local time or UTC?
        #     for hw, sensor_list in self.sensors.values():
        #         # is there a sensor that needs to be read now?
        #         for sensor in sensor_list:
        #             if sensor.next_read == now:
        #                 hw.read()
        #                 break
        #         # ok, let's get the sensors reading from their hardware and set them for their next reading time
        #         for sensor in sensor_list:
        #             if sensor.next_read == now:
        #                 sensor.calculate_value()
        #                 print(sensor.name, sensor.calculated_value)
        #                 sensor.db_rec["calculated_value"] = sensor.calculated_value
        #                 self.log.add_log(self.name, system_name="Horizon 1", param=sensor.db_rec)
        #                 sensor.next_read = sensor.cron.get_next(datetime).strftime("%Y-%m-%d %H:%M")
        #                 if DEBUG:
        #                     print(sensor.name, "next read at:", sensor.next_read)
        #
        #     while now == datetime.now().strftime("%Y-%m-%d %H:%M"):
        #         sleep(10)





def exist_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.isfile(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sqlite", dest="dbfilename", help="Path of a Sqlite3 database.")  # type=exist_file, # required=False,
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()

    if args.dbfilename:
        db = Ponicwatch_db("sqlite3", [args.dbfilename])
        ctrl = Controller(db)
        ctrl.run()
    else:
        print("currently: -s dbfilename is mandatory")
