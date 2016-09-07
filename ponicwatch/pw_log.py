#!/bin/python3
"""
    Model for the table tb_log
    Created by Eric Gibert on 2 May 2016

    A log entry is created by a controller. The controller is identified by its name.
    A controller might log various log type:
    - SENSOR: log a sensor input/reading
    - SWITCH: log a switch state (usually when there is a change of state)
    - INFO: log an information message
    - WARNING: log a warning message, action might be required by an operator
    - ERROR: log an error message, an email should be trigger to raise an alarm to an operator
"""
import json
from datetime import datetime, timezone

from model.model import Ponicwatch_Table
from sensor import Sensor
from switch import Switch


class Ponicwatch_Log(Ponicwatch_Table):
    """
    Class to manage the table tb_log i.e. adding new record and retrieve exist ones
    'object_id':
        - When a Sensor or a Switch data is recorded then its id is used as 'object_id'
        - When a message (info/warning/error) is recorded then an application id is given i.e. like an error code

    The system name is provided when relevant (sensor, switch, other) or left empty if not relevant.

    For Switches and Sensors:
        - float_value: current value
        - text_value: JSON representation of the object

    For messages:
        - float_value: relevant value like a threshold or -1.0 if not relevant
        - text_value: message

    'created_on": timestamp when the log record has been created. A log record cannot be updated.
    """
    LOG_TYPE = {
        #
        "UNKNOWN": 0,
        # hardware/peripherics
        "SENSOR": 1,
        "SWITCH": 2,
        # messages
        "INFO": 10,
        "WARNING": 11,
        "ERROR": 12,
    }

    META = {"table": "tb_log",
            "id": "log_id",
            "columns": (
                            "log_id", # INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            "controller_name", # TEXT NOT NULL,
                            "log_type", # TEXT NOT NULL,
                            "object_id", # INTEGER NOT NULL,
                            "system_name", # TEXT NOT NULL,
                            "float_value", # REAL NOT NULL DEFAULT (0.0),
                            "text_value", # TEXT,
                            "created_on", # TIMESTAMP NOT NULL
                        )
            }

    def __init__(self, controller, debug=False, *args, **kwargs):
        super().__init__(controller.db, Ponicwatch_Log.META, *args, **kwargs)
        self.debug = debug
        self.controller_name = controller.name

    @staticmethod
    def json_exception(o):
        if isinstance(o, datetime):
            return o.isoformat()

    def add_log(self, log_type=None, system_name="", param=None):
        """
        Add an entry in tb_log.
        :param log_type: optional, given for the message type (info, warning, error) else the param type will be used to find it
        :param system_name: optional
        :param param:
            - message: a dictionary for { 'error_code', 'float_value', 'text_value' }
            - switch/sensor: object itself to get its values as a JSON string
        :return: log_id if INSERT is successful or None
        """
        # MESSAGE:
        # log_type is mandatory to know the message level (info/warning/error)
        # param is a dictionary
        if log_type in ["INFO", "WARNING", "ERROR"]:
            self.insert(controller_name=self.controller_name,
                        log_type=Ponicwatch_Log.LOG_TYPE[log_type],
                        object_id=param["error_code"],
                        system_name=system_name,
                        float_value=param["float_value"] if "float_value" in param else -1.0,
                        text_value=param["text_value"],
                        created_on=datetime.now(timezone.utc)
                        )
            if self.debug:
                print(log_type, param["error_code"], param["text_value"]) 
        elif isinstance(param, Switch):
            self.insert(controller_name=self.controller_name,
                        log_type=Ponicwatch_Log.LOG_TYPE["SWITCH"],
                        object_id=param["switch_id"],
                        system_name=system_name,
                        float_value=float(param["value"]),
                        text_value=json.dumps(param, skipkeys=True, default=Ponicwatch_Log.json_exception),
                        created_on=datetime.now(timezone.utc)
                        )
            if self.debug:
                print("SWITCH", param["switch_id"], param["name"], param["value"])            
        elif isinstance(param, Sensor):
            self.insert(controller_name=self.controller_name,
                        log_type=Ponicwatch_Log.LOG_TYPE["SENSOR"],
                        object_id=param["sensor_id"],
                        system_name=system_name,
                        float_value=float(param["calculated_value"]),
                        text_value=json.dumps(param, skipkeys=True, default=Ponicwatch_Log.json_exception),
                        created_on=datetime.now(timezone.utc)
                        )
            if self.debug:
                print("SENSOR", param["sensor_id"], param["name"], param["calculated_value"])

    def add_info(self, msg, err_code=0, fval=0.0):
        """Helper function for the controller to log an INFO message"""
        self.add_log("INFO", "controller", {'error_code': err_code, 'float_value': fval, 'text_value': msg})
    def add_warning(self, msg, err_code=0, fval=0.0):
        """Helper function for the controller to log a WARNING message"""
        self.add_log("WARNING", "controller", {'error_code': err_code, 'float_value': fval, 'text_value': msg})
    def add_error(self, msg, err_code=0, fval=0.0):
        """Helper function for the controller to log an ERROR message"""
        self.add_log("ERROR", "controller", {'error_code': err_code, 'float_value': fval, 'text_value': msg})

    def __str__(self):
        return "[{}] {}".format(self.controller_name, self["text_value"])