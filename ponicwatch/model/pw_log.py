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
from datetime import datetime, timezone
import json
from .switch import Switch
from .sensor import Sensor

class Ponicwatch_log(dict):
    """
    Class to manage the table tb_log i.e. adding new record and retrieve exist ones
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

    _tb_log = (
        "log_id", # INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "controller_name", # TEXT NOT NULL,
        "log_type", # TEXT NOT NULL,
        "object_id", # INTEGER NOT NULL,
        "system_name", # TEXT NOT NULL,
        "float_value", # REAL NOT NULL DEFAULT (0.0),
        "text_value", # TEXT,
        "created_on", # TIMESTAMP NOT NULL
    )

    def __init__(self, db, id=None, debug=False, *args,**kwargs):
        """Model to access the _tb_log table
        - db: the database containinng the log table
        - id: optional: fetch on log entry"""
        dict.__init__(self, *args, **kwargs)
        self.db = db
        self.debug = debug
        for col in Ponicwatch_log._tb_log:
            self[col] = None
        if id:
            self.get_log(id=id)

    def get_log(self, id=None):
        """
        Fetch one record from tb_log matching either of the given parameters
        :param id: tb_switch.switch_id (int)
        """
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                if id and type(id) is int:
                    curs.execute("SELECT * from tb_log where log_id=?", (id,))
                else:
                    raise ValueError
                log_row = curs.fetchall()
                if len(log_row) == 1:
                    for idx, col in enumerate(Ponicwatch_log._tb_log):
                        self[col] = log_row[0][idx]
            finally:
                curs.close()

    @staticmethod
    def json_exception(o):
        if isinstance(o, datetime):
            return o.isoformat()

    def add_log(self, controller_name, log_type=None, system_name="", param=None):
        """
        Add an entry in tb_log.
        :param controller_name: mandatory
        :param log_type: optional, given for the message type (info, warning, error) else the param type will be used to find it
        :param system_name: optional
        :param param:
            - message: a dictionary for { 'error_code', 'float_value', 'text_value' }
            - switch/sensor: object itself to get its values as a JSON string
        :return: log_id if INSERT is successful or None
        """
        new_id = -1
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                # MESSAGE:
                # log_type is mandatory to know the message level (info/warning/error)
                # param is a dictionary
                if log_type in ["INFO", "WARNING", "ERROR"]:
                    curs.execute("""INSERT INTO tb_log( controller_name,
                                                        log_type,
                                                        object_id,
                                                        system_name,
                                                        float_value,
                                                        text_value,
                                                        created_on
                                                      ) values(?,?,?,?,?,?,?)""",
                                 (controller_name,
                                  Ponicwatch_log.LOG_TYPE[log_type],
                                  param["error_code"],
                                  system_name,
                                  param["float_value"] if "float_value" in param else -1.0,
                                  param["text_value"],
                                  datetime.now(timezone.utc)
                                 ))
                elif isinstance(param, Switch):
                    curs.execute("""INSERT INTO tb_log( controller_name,
                                           log_type,
                                           object_id,
                                           system_name,
                                           float_value,
                                           text_value,
                                           created_on
                                         ) values(?,?,?,?,?,?,?)""",
                                 (controller_name,
                                  Ponicwatch_log.LOG_TYPE["SWITCH"],
                                  param["switch_id"],
                                  system_name,
                                  float(param["value"]),
                                  json.dumps(param, skipkeys=True, default=Ponicwatch_log.json_exception),
                                  datetime.now(timezone.utc)
                                  ))
                elif isinstance(param, Sensor):
                    curs.execute("""INSERT INTO tb_log( controller_name,
                                           log_type,
                                           object_id,
                                           system_name,
                                           float_value,
                                           text_value,
                                           created_on
                                         ) values(?,?,?,?,?,?,?)""",
                                 (controller_name,
                                  Ponicwatch_log.LOG_TYPE["SENSOR"],
                                  param["sensor_id"],
                                  system_name,
                                  float(param["calculated_value"]),
                                  json.dumps(param, skipkeys=True, default=Ponicwatch_log.json_exception),
                                  datetime.now(timezone.utc)
                                  ))
                new_id = curs.lastrowid
            finally:
                curs.close()
        if new_id>=0:
            self.get_log(new_id)
        if self.debug:
            print(str(self))
        return new_id

    def add_info(self, msg, err_code=0, fval=0.0):
        """Helper function for the controller to log an INFO message"""
        self.add_log(self["controller_name"], "INFO", "controller",
                     {'error_code': err_code, 'float_value': fval, 'text_value': msg})
    def add_warning(self, msg, err_code=0, fval=0.0):
        """Helper function for the controller to log a WARNING message"""
        self.add_log(self["controller_name"], "WARNING", "controller",
                     {'error_code': err_code, 'float_value': fval, 'text_value': msg})
    def add_error(self, msg, err_code=0, fval=0.0):
        """Helper function for the controller to log an ERROR message"""
        self.add_log(self["controller_name"], "ERROR", "controller",
                     {'error_code': err_code, 'float_value': fval, 'text_value': msg})

    def __str__(self):
        return "[{}] {}".format(self["controller_name"], self["text_value"])