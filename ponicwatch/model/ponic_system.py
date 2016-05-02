#!/bin/python
"""
  Model for the table tb_system
  A system represents an hydroponic/aquaponic/aeroponic system.

  Note: 'Atmosphere' can be a system to link sensor like temperature, humidity, etc
"""

class Ponic_System(dict):
    """
      name: to identify the system easily withion an area
      location: where is the system installed
      sys_type: NFT, aeroponic, Ebb and Flow, etc
      nb_plants:  *important* number of plants is necessary to track the timing of plantations --> to do list
    """

    _tb_system = (
        "system_id", # INTEGER NOT NULL,
        "name", # TEXT NOT NULL,
        "location", # TEXT,
        "nb_plants", # INTEGER NOT NULL DEFAULT (0),
        "sys_type", # TEXT
    )

    def __init__(self, db, name=None, *args,**kwargs):
        dict.__init__(self, *args, **kwargs)
        self.db = db
        for col in Ponic_System._tb_system:
            self[col] = None
        if name:
            self.get_system(name)

    def get_system(self, name=None, id=None):
        """
        Fetch one record in tb_system matching the given parameters
        :param name: tb_system.name
        """
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                if name and type(name) is str:
                    curs.execute("SELECT * from tb_system where name=?", (name, ))
                elif id and type(id) is int:
                    curs.execute("SELECT * from tb_system where system_id=?", (id,))
                else:
                    raise ValueError
                sys_row = curs.fetchall()
                if len(sys_row) == 1:
                    for idx, col in enumerate(Ponic_System._tb_system):
                        self[col] = sys_row[0][idx]
            finally:
                curs.close()

    def __str__(self):
        return "{} ({})".format(self["name"], self["location"])