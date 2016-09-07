#!/bin/python3
"""
    Model for the table tb_switch.
    Created by Eric Gibert on 29 Apr 2016

    Swicthes are objects linked to a hardware pin (with or without a relay) to control an piece of equipement (pump, light,...).
    They belong to one Controller that controls their state.
    A switch is either set manually ON/OFF while in AUTO mode,the controler will tabulate the current time on the 'timer' string.
"""
from datetime import datetime, timezone
from model.model import Ponicwatch_Table

class Switch(Ponicwatch_Table):
    """
    - 'switch_id' and 'name' identify uniquely a switch within a Controller database.
    - 'mode': indicates if the switch should be 'ON' or 'OFF' or 'AUTO'
        * at starting time, a switch of mode 'ON' will be set on, 'OFF' will be turn off (default)
        * in 'AUTO' mode, the state of the switch is define by the current time tabulated in the 'timer' sting --> 0 = OFF, 1 = OFF
    - 'value': current state of the switch ( 0 = OFF, 1 = OFF )
    - 'hardware': identification of the hardware undelying the switch. Usually a pin number within an IC.
    - 'timer': list of 0 (OFF) and 1 (ON), each representing a position for a given time.
    - 'timer_interval': duration in  minutes of one timer unit, usually 15 minutes.
    """
    MODE = {
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
                         "hardware", #  TEXT NOT NULL,
                         "timer", #  TEXT NOT NULL,
                         "value", #  INTEGER NOT NULL DEFAULT (0),
                         "timer_interval", #  INTEGER NOT NULL DEFAULT (15),
                         "updated_on", #  TIMESTAMP,
                         "synchro_on", #  TIMESTAMP
                        )
            }

    def __init__(self, controller, system_name, hardware, *args, **kwargs):
        super().__init__(controller.db, Switch.META, *args, **kwargs)
        self.controller = controller
        self.hardware = hardware
        self.system_name = system_name + "/" + self["name"]

    def get_record(self, id=None, name=None):
        """
        Fetch one record from tb_switch matching either of the given parameters
        :param name: tb_switch.name (string)
        :param id: tb_switch.switch_id (int)
        """
        super().get_record(id, name)
        self.hw_components = self["hardware"].split('.')  # example:"AM2302.4.T" --> ['AM2302', '4', 'T']
        self.IC, self.pins = self.hw_components[0], self.hw_components[1]
        self.hw_id = self.IC + '.' + self.pins #  like "AM2302.4"  pin 4 on chip AM2302

    def execute(self):
        """on timer/scheduler"""
        pass

    def update_value(self, value):
        self.update(alue=value, updated_on=datetime.now(timezone.utc))

    @classmethod
    def all_keys(cls, db):
        return super().all_keys(db, Switch.META)

    def __str__(self):
        return "{} ({})".format(self["name"], Switch.MODE[self["mode"]])