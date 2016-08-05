#!/bin/python3
"""
  A system is usually an hydroponic/acquaponic system for which one wamts to monitor various parameters
  like water temperature, pH, EC, etc..
  The atmosphere can be assimilated to a system too in order to montor air temperature and humidity for example.
"""



class System(dict):

    _tb_system = (
        "system_id",  # INTEGER NOT NULL,
        "name",  # TEXT NOT NULL,
        "location",  # TEXT,
        "nb_plants",  # INTEGER NOT NULL DEFAULT(0),
        "sys_type"  # TEXT
    )

    def __init__(self, db, *args,**kwargs):
        """Select one record from the """
        dict.__init__(self, *args, **kwargs)
        self.db = db
        for col in System._tb_system:
            self[col] = None
