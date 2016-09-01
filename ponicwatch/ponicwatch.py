#!/usr/bin/env python3
"""
    Created by Eric Gibert on 12 May 2016

    Controller
"""
import argparse
import os.path
from time import sleep
from threading import BoundedSemaphore
from apscheduler.schedulers.background import BackgroundScheduler

from system import System
from model.pw_db import Ponicwatch_Db
from pw_log import Ponicwatch_Log
from user import User
from sensor import Sensor
from switch import Switch
from hardware import Hardware

DEBUG = True  # activate the Debug mode or not

class Controller(object):
    """The Controller in a MVC model"""

    def __init__(self, db):
        """- Create the controller, its Viewer and connect to database (Model)
           - Select all the hardware (sensors/switches) for the systems under its control
           - Launch the scheduler
        """
        # keep a link to the database i.e. M in MVC
        self.db = db
        self.db.exclusive_access = BoundedSemaphore(value=1)
        # finding the Controller User entry --> currently 'hard coded' as 'ctrl'/'passwd' --> to improve later
        self.user = User(self)
        self.user.get_user("ctrl", "passwd")
        self.name = self.user["name"]  # this name is used to identify the log messages posted by this controller

        # opening the LOGger with the debug level for this application run
        self.log = Ponicwatch_Log(controller=self, debug=DEBUG)

        # Create the background scheduler that will execute the actions (using the APScheduler library)
        self.scheduler = BackgroundScheduler()

        # select all the systems, sensors, switches to monitor and the hardware drivers
        self.systems, self.sensors, self.switches, self.hardwares = {}, {}, {}, {}
        self.db.open()
        try:
            self.db.curs.execute("SELECT * from tb_link where system_id > 0 order by system_id, sensor_id, switch_id")
            self.links = self.db.curs.fetchall()
        finally:
            self.db.close()
        for system_id, sensor_id, switch_id, hardware_id in self.links:
            # (1) create all necessary objects
            # (2) and register the system and hardware to a sensor/switch
            new_switch_or_sensor = None
            if system_id not in self.systems:
                self.systems[system_id] = System(self, id=system_id)
            if hardware_id and hardware_id not in self.hardwares:
                self.hardwares[hardware_id] = Hardware(self, id=hardware_id)

            if sensor_id and sensor_id not in self.sensors:
                    new_switch_or_sensor = self.sensors[sensor_id] = Sensor(controller=self,
                                                                            id=sensor_id,
                                                                            system_name=self.systems[system_id]["name"],
                                                                            hardware=self.hardwares[hardware_id])
            if switch_id and switch_id not in self.switches:
                    new_switch_or_sensor = self.switches[switch_id] = Switch(controller=self,
                                                                             id=switch_id,
                                                                             system_name=self.systems[system_id]["name"],
                                                                             hardware=self.hardwares[hardware_id])

            # When do we need to read the sensor or activate a switch?
            # ┌───────────── min (0 - 59)
            # │ ┌────────────── hour (0 - 23)
            # │ │ ┌─────────────── day of month (1 - 31)
            # │ │ │ ┌──────────────── month (1 - 12)
            # │ │ │ │ ┌───────────────── day of week (0 - 6) (0 to 6 are Sunday to
            # │ │ │ │ │                  Saturday, or use names; 7 is also Sunday)
            # │ │ │ │ │
            # │ │ │ │ │
            # * * * * *
            if new_switch_or_sensor:
                min, hrs, dom, mon, dow = new_switch_or_sensor["timer"].split()  # like "*/5 * * * *" --> every 5 minutes
                self.scheduler.add_job(new_switch_or_sensor.execute, 'cron', second=min, hour=hrs, day=dom, month=mon, day_of_week=dow)

    def run(self):
        """Starts the APScheduler task"""
        self.running = True
        self.scheduler.start()
        self.log.add_info("Controller is now running.")
        try:
            # This is here to simulate application activity (which keeps the main thread alive).
            while self.running :
                sleep(2)
        except (KeyboardInterrupt, SystemExit):
            # Not strictly necessary if daemonic mode is enabled but should be done if possible
            self.scheduler.shutdown()
        self.log.add_info("Controller has been stopped.")


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
        db = Ponicwatch_Db("sqlite3", {'database': args.dbfilename})
        ctrl = Controller(db)
        ctrl.run()
    else:
        print("currently: -s dbfilename is mandatory")
