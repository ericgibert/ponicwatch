#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Created by Eric Gibert on 12 May 2016

    Controller
"""
import sys, os
import argparse
import signal
import json
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import SchedulerNotRunningError
from datetime import datetime

try:
    import pigpio
    _simulation = False
except ImportError:
    _simulation = True
import pigpio_simu

from model.pw_db import Ponicwatch_Db
from system import System
from pw_log import Ponicwatch_Log
from user import User
from sensor import Sensor
from switch import Switch
from hardware import Hardware
from interrupt import Interrupt
from http_view import http_view, get_image_file, one_pw_object_html, stop as bottle_stop, default as http_default
from send_email import send_email

__version__ = "2.20190409 Seattle"
__author__ = 'Eric Gibert'
__license__ = 'MIT'

# activate the Debug mode: messages on the screen with print() functions
# 3: all messages ; 2: Error and Warnings ; 1: Error level ; 0: no messages
# command line can pass this [0..3] value too with option --debug / -d
DEBUG = 0

class Controller(object):
    """The Controller in a MVC model"""

    def __init__(self, db, bottle_ip='127.0.0.1', pigpio_host="", pigpio_port=8888):
        """- Create the controller, its Viewer and connect to database (Model)
           - Select all the hardware (sensors/switches) for the systems under its control
           - Launch the scheduler
           - host:port is used to connect to the pigpio server running on the Raspberry Pi.
           Need to execute 'sudo pigpiod' to get that daemon running if it is not automatically started at boot time

           :param db: instance of a Ponicwatch_Db
           :param bottle_ip: IP to reach the webpages. Important to set properly for remote access.
        """
        global _simulation # if no PGIO port as we are not running on a Raspberry Pi
        self.debug = DEBUG
        self.bottle_ip = bottle_ip
        # keep a link to the database i.e. M in MVC
        self.db = db
        self.db.allow_close = False
        # finding the Controller User entry --> currently 'hard coded' as 'ctrl'/'passwd' --> to improve later
        self.user = User(self, id=1)
        self.name = self.user["name"]  # this name is used to identify the log messages posted by this controller

        # opening the LOGger with the debug level for this application run
        self.log = Ponicwatch_Log(controller=self, debug=DEBUG)

        # Create the background scheduler that will execute the actions (using the APScheduler library)
        self.scheduler = BackgroundScheduler()

        # select all the systems, sensors, switchs to monitor and the necessary hardware drivers
        self.pig = pigpio.pi(pigpio_host, pigpio_port) if not _simulation else pigpio_simu.pi()
        if not self.pig.connected:
            if self.debug >= 2: print("WARNING: not connected to a RasPi")
            self.pig = pigpio_simu.pi()
            _simulation = True
        # some plural are "fake" to respect the logic of: <cls name> + 's' --> dictionary of <cls> PonicWatch Object
        self.systems, self.sensors, self.switchs, self.hardwares, self.interrupts = {}, {}, {}, {}, {}
        # system_id <= 0:  inactive link --> ignore this row
        self.db.curs.execute("SELECT * from tb_link where system_id > 0 order by system_id desc, order_for_creation")
        self.links = self.db.curs.fetchall()
        for system_id, sensor_id, switch_id, hardware_id, order_for_creation, interrupt_id in self.links:
            # (1) create all necessary objects
            # (2) and register the system and hardware to a sensor/switch
            if system_id not in self.systems:
                self.systems[system_id] = System(self, id=system_id)
            if hardware_id and hardware_id not in self.hardwares:
                self.hardwares[hardware_id] = Hardware(controller=self,
                                                       id=hardware_id,
                                                       system_name=self.systems[system_id]["name"])
            if sensor_id and sensor_id not in self.sensors:
                    self.sensors[sensor_id] = Sensor(controller=self,
                                                     id=sensor_id,
                                                     system_name=self.systems[system_id]["name"],
                                                     hardware=self.hardwares[hardware_id])
            if switch_id and switch_id not in self.switchs:
                    self.switchs[switch_id] = Switch(controller=self,
                                                     id=switch_id,
                                                     system_name=self.systems[system_id]["name"],
                                                     hardware=self.hardwares[hardware_id])

            if interrupt_id and interrupt_id not in self.interrupts:
                self.interrupts[interrupt_id] = Interrupt(controller=self,
                                                          id=interrupt_id,
                                                          system_name=self.systems[system_id]["name"],
                                                          hardware=self.hardwares[hardware_id])
        self.db.allow_close = True
        self.db.close()

    def add_cron_job(self, callback, timer):
        """
        Add a new scheduled task
        :param callback:
        :param timer:  a string '* * * * * *' OR a JSON object as { 't': ['* * * * * *', t2, t3...]}
        :return:
        """
        if timer[0]=='{':
            # convert the JSON timer string to a python dictionary
            try:
                cron_times = json.loads(timer)
                cron_times = cron_times['t']
            except:  # json.JSONDecodeError:
                print("Alarm: timer is not a JSON string!", timer)
        else:
            cron_times = [timer]
        i = 0.0
        for cron_time in cron_times:
            # When do we need to read the sensor or activate a switch?
            # ┌───────────── sec (0 - 59)
            # | ┌───────────── min (0 - 59)
            # | │ ┌────────────── hour (0 - 23)
            # | │ │ ┌─────────────── day of month (1 - 31)
            # | │ │ │ ┌──────────────── month (1 - 12)
            # | │ │ │ │ ┌───────────────── day of week (0 - 6) (0 to 6 are Sunday to
            # | │ │ │ │ │                  Saturday, or use names; 7 is also Sunday)
            # | │ │ │ │ │
            # | │ │ │ │ │
            # * * * * * *
            _sec, _min, _hrs, _dom, _mon, _dow = cron_time.split()  # like "*/5 * * * * *" --> every 5 seconds
            self.scheduler.add_job(callback, 'cron', second=_sec, minute=_min, hour=_hrs, day=_dom, month=_mon, day_of_week=_dow)
            self.log.add_log(log_type='SCHEDULER', system_name='@startup',
                            param={ 'error_code':0, 'text_value': cron_time, 'float_value':i})
            i += 1.0

    def run(self):
        """Starts the APScheduler task and the Bottle HTTP server"""
        self.running = True
        with open("ponicwatch.pid", "wt") as fpid:
            print(os.getpid(), file=fpid)

        def stop_handler(signum, frame):
            """ allow:   kill -10 `cat ponicwatch.pid`   """
            self.stop()
            sys.exit()
        signal.signal(signal.SIGUSR1, stop_handler)

        self.scheduler.start()
        self.log.add_info("Controller {} is now running.".format(__version__), fval=1.0)
        # http_view.controller = self
        try:
            http_view.run(host=self.bottle_ip)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self.stop()

    def stop(self, from_bottle=False):
        try:
            self.scheduler.shutdown()  # Not strictly necessary if daemonic mode is enabled but should be done if possible
        except SchedulerNotRunningError:
            pass
        for hw in self.hardwares.values():
            hw.cleanup()
        self.log.add_info("Controller {} has been stopped.".format(__version__), fval=0.0)
        if not from_bottle: bottle_stop()

    # if_expression manipulation to provide conditional execution to PWO based on their 'if' string
    def make_expression(self, submitted_by, if_expression):
        """Replace the Sensor/Switch/Hardware reference to its value
        Error will be caught by the calling function: SyntaxError, ValueError, NameError
        :param submitted_by: the pwo requesting the 'if_expression' evalution (needed for logging in case of error)
        :param if_expression: string or tuple from the 'init' dictionary under the key 'if'
        :return result: python evaluation of the input string with all pwo references have been replaced by their value
        """
        if isinstance(if_expression, str):
            # expects a string starting by a pwo reference and then a boolean test
            # ex: "Sensor[2]>=40.0" or "Switch[1]==0"
            pwo_cls, _ = if_expression.split('[', 1)
            id, test = _.split(']', 1)
            pwo = self.get_pwo(pwo_cls, id)
            try:
                _expression = str(pwo.value) + test  # if the direct read is possible then use it
            except AttributeError:
                _expression = str(pwo["value"]) + test  # else take the latest read value
        elif isinstance(if_expression, list):
            # expects list: format string followed by the pwo references or keyword 'now'
            # example: [ "{}>10. and {}==1", "Sensor[1]", "Switch[2]" ]
            _format, pwo_values = if_expression[0], []
            for pwo_ref in if_expression[1:]:
                if pwo_ref.lower() == "now":
                    pwo_values.append(datetime.now())  # expects {:%H} for hour --> "8<={:%H}<=20".format(datetime.now())
                else:
                    pwo_cls, id = pwo_ref.split('[', 1)
                    pwo = self.get_pwo(pwo_cls, id[:-1]) # drop the last ']'
                    try:
                        pwo_values.append(pwo.value)
                    except AttributeError:
                        pwo_values.append(pwo["value"])
            _expression = _format.format(*pwo_values)
        else:
            msg = "Error! Unknown if_expression type: {} for {}".format(type(if_expression), submitted_by)
            self.log.add_error(msg=msg, err_code=submitted_by["id"], fval=-2.6)
            _expression = None
        return _expression

    def eval_expression(self, submitted_by, if_expression, make_expression=None):
        """evaluate the expression found in the init_dit['if'] of a PWO"""
        try:
            _expression = make_expression or self.make_expression(submitted_by, if_expression)
            result = eval(_expression)
        except (SyntaxError, NameError, ValueError) as err:
            self.log.add_error(msg="if_expression {} cannot be evaluated: {} for {}".format(if_expression, err, submitted_by),
                                  err_code=submitted_by["id"], fval=-2.7)
            result = None

        if self.debug >= 3:
            print("eval({}) == {}".format(_expression, result))
        return result

    ### helper functions
    def get_pwo(self, cls, id):
        """return a PonicWatch Object from the controller's PWO dictionary
        :param cls: either a string as class name or an PW object
        :param id: the pwo's id, must be integer as pwo dictionary key
        :return pwo: the matching pwo or None
        """
        pwo_dict_name = (cls if isinstance(cls, str) else cls.__class__.__name__).lower() + 's'
        pwo_dict = getattr(self, pwo_dict_name)
        pwo = None
        try:
            pwo = pwo_dict[int(id)]
        except KeyError:
            msg = "No pwo id {} found in {}".format(id, pwo_dict_name)
            if self.debug >= 3:
                print(msg)
            self.log.add_error(msg=msg, err_code=id, fval=-1.1)
        return pwo

    def print_list(self):
        """CLI: Print the list of all created objects in the __init__ phase"""
        print("--- System ---")
        for k,v in self.systems.items(): print(k,v)
        print("--- Hardware ---")
        for k,v in self.hardwares.items(): print(k,v, v["init"])
        print("--- Switches ---")
        for k,v in self.switchs.items(): print(k, v, v["init"])
        print("--- Sensors ---")
        for k,v in self.sensors.items(): print(k,v, v["init"])
        print("--- Interruptions ---")
        for k,v in self.interrupts.items(): print(k,v)
        print("--- Links ---")
        for system_id, sensor_id, switch_id, hardware_id, order_for_creation, interrupt_id in self.links:
            print("system_id", system_id or '-',
                  "hardware_id", hardware_id or '-',
                  "switch_id", switch_id or '-',
                  "sensor_id", sensor_id or '-',
                  "interrupt_id", interrupt_id or '-', sep='\t')

    def ponicwatch_notification(self):
        """
        Regular email to inform the system manager of its status
        :return:
        """
        images = []     # list of .png to attach to the email
        html = http_default()       # email's body
        objects = []    # working list of all Ponicwatch objects (pwo)
        for s in self.systems.values(): objects.append(s)
        for s in self.switchs.values(): objects.append(s)
        for s in self.sensors.values(): objects.append(s)
        for pwo in objects:
            html += one_pw_object_html(pwo, only_html=True)
            if os.path.isfile(get_image_file(pwo)):
                images.append(get_image_file(pwo))
        # print(html)
        send_email("Ponicwatch Notification - %s" % ",".join([s["name"] for s in self.systems.values()]),
                   from_=self.user["email"],
                   to_=["ericgibert@yahoo.fr", ],
                   message_HTML=html,
                   images=images,
                   login=self.user["email"],
                   passwd=self.user["password"])


def exist_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.isfile(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sqlite", dest="dbfilename", help="Path of a Sqlite3 database.", type=exist_file, required=True),
    parser.add_argument("-p", "--pigpio",  dest="pigpio", help="Optional: remote Raspberry Pi (pigpio) IP address", required=False, default="")
    parser.add_argument("-b", "--bottle", dest="bottle_ip", help="Optional: Raspberry Pi IP address to allow remote connections", required=False,  default="127.0.0.1")
    parser.add_argument("-d", "--debug",  dest="debug", help="Optional: debug level [0..3]", required=False, type=int, default=None)
    parser.add_argument("-l", "--list",   dest="print_list", help="List all created objects - no running -", action='store_true')
    parser.add_argument("-c", "--clean",  dest="cleandb", help="Clean database tables/logs", action='store_true', default=False)
    parser.add_argument("-n", "--notification", dest="notification", help="Sends notification email", action='store_true', default=False)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()
    if isinstance(args.debug, int):
        DEBUG = args.debug

    if args.dbfilename:
        db = Ponicwatch_Db("sqlite3", {'database': args.dbfilename}, args.cleandb)
        ctrl = Controller(db, bottle_ip=args.bottle_ip, pigpio_host=args.pigpio)
        http_view.controller = ctrl
        if args.print_list:
            ctrl.print_list()
        elif args.notification:
            ctrl.ponicwatch_notification()
        else:
            ctrl.run()
    else:
        print("currently: -s dbfilename is mandatory")
