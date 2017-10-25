#!/bin/python3
"""
    Model for the table tb_switch.
    Created by Eric Gibert on 29 Apr 2016

    Swicthes are objects linked to a hardware pin (with or without a relay) to control an piece of equipement (pump, light,...).
    They belong to one Controller that controls their state.
    A switch is either set manually ON/OFF while in AUTO mode,the controler will tabulate the current time on the 'timer' string.
"""
from model.model import Ponicwatch_Table

class Switch(Ponicwatch_Table):
    """
    - 'switch_id' and 'name' identify uniquely a switch within a Controller database.
    - 'mode': indicates if the switch should be 'ON' or 'OFF' or 'AUTO'
        * at starting time, a switch of mode 'ON' will be set on, 'OFF' will be turn off (default)
        * in 'AUTO' mode, the scheduler assign the 'set_value_to' given in the 'init' dictionary to the pin
    - 'value': current state of the switch ( 0 = OFF, 1 = OFF )
    - 'init': identification of the hardware undelying the switch. Usually a pin number within an IC.
    - 'timer': cron like string to define the execution timing patterns
    - 'timer_interval': duration in  minutes of one timer unit, usually 15 minutes.
    """
    MODE = {
       -1: "INACTIVE",    # switch to be ignored
        0: "OFF",    # either the switch mode or the timer off
        1: "ON",     # either the switch mode or the timer on
        2: "AUTO",   # switch mode to automatic i.e. relies on current time & 'timer' to know the current value
    }

    META = {"table": "tb_switch",
            "id": "switch_id",
            "columns": (
                         "switch_id", # INTEGER NOT NULL,
                         "name", #  TEXT NOT NULL,
                         "mode", #  INTEGER NOT NULL DEFAULT (0),
                         "init", #  TEXT NOT NULL,
                         "timer", #  TEXT NOT NULL,
                         "value", #  INTEGER NOT NULL DEFAULT (0),
                         "timer_interval", #  INTEGER NOT NULL DEFAULT (15),
                         "updated_on", #  TIMESTAMP,
                         "synchro_on", #  TIMESTAMP
                        )
            }

    def __init__(self, controller, system_name, hardware, db=None, *args, **kwargs):
        super().__init__(db or controller.db, Switch.META, *args, **kwargs)
        self.controller = controller
        self.hardware = hardware
        #if hardware["mode"] == 2:  # R/W
        if self["mode"] > self.INACTIVE:
            self.hardware.set_pin_as_output(self.init_dict["pin"])
            self.system_name = system_name + "/" + self["name"]
            if self["timer"]:
                self.controller.add_cron_job(self.execute, self["timer"])
            # set the switch to 'set_value_to' if given in the init dictionary else to the last value recorded
            # try:
            #     self.execute(self.init_dict["set_value_to"])
            # except KeyError:
            #     self.execute(self.init_dict["value"])


    def execute(self, given_value=None):
        """
        On timer/scheduler: no 'given_value' hence set the pin to the 'set_value_to' found in the 'init' dictionary
        Else direct call: the pin is set to the 'given_value' if provided else the 'set_value'to' is used
        """
        self.hardware.write(self.init_dict["pin"], given_value or self.init_dict["set_value_to"])
        self.update(value=given_value or self.init_dict["set_value_to"])
        self.controller.log.add_log(system_name=self.system_name, param=self)

    @classmethod
    def all_keys(cls, db):
        return super().all_keys(db, Switch.META)

    def __str__(self):
        return "{} ({})".format(self["name"], Switch.MODE[self["mode"]])
