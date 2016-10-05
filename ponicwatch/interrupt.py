#!/bin/python3
"""
  An interrupt is defined by:
  - a trigger --> usually a pin on a IC
  - a threshold --> LOW, HIGH or float
  Once both conditions are fulfilled then a callback function is called
"""

from model.model import Ponicwatch_Table

class Interrupt(Ponicwatch_Table):
    """
    - name: to identify the system easily withion an area
    - location: where is the system installed
    - sys_type: NFT, aeroponic, Ebb and Flow, etc
    - nb_plants:  *important* number of plants is necessary to track the timing of plantations --> to do list
    """
    META = {"table": "tb_interrupt",
            "id": "interrupt_id",
            "columns": (
                "interrupt_id", # INTEGER NOT NULL,
                "name", # TEXT NOT NULL,
                "hardware", # TEXT NOT NULL,
                "init" , #TEXT,
                "threshold", # INTEGER NOT NULL DEFAULT (0),
                "updated_on", # TIMESTAMP,
                "synchro_on", # TIMESTAMP
                )
            }

    def __init__(self, controller, *args, **kwargs):
        super().__init__(controller.db, Interrupt.META, *args, **kwargs)

    def __str__(self):
        return "{} ({})".format(self["name"], self["hardware"])
