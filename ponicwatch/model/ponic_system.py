#!/bin/python
"""
  Model for the table tb_system
  A system represents an hydroponic/aquaponic/aeroponic system.

  Note: 'Atmosphere' can be a system to link sensor like temperature, humidity, etc
"""

class Ponic_System(object):
    """
      name: to identify the system easily withion an area
      location: where is the system installed
      sys_type: NFT, aeroponic, Ebb and Flow, etc
      nb_plants:  *important* number of plants is necessary to track the timing of plantations --> to do list
    """
    def __init__(self, db, name=None):
        self.db = db
        self.system_id, self.name, self.location, self.nb_plants, self.sys_type = None, None, None, None, None
        if name:
            self.get_system(name)

    def get_system(self, name):
        """
        Fetch one record in tb_system matching the given parameters
        :param name: tb_system.name
        """
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                curs.execute("SELECT * from tb_system where name=?", (name, ))
                sys_row = curs.fetchall()
                if len(sys_row) == 1:
                    self.system_id, self.name, self.location, self.nb_plants, self.sys_type = sys_row[0]
            finally:
                curs.close()

    def __str__(self):
        return "{} ({})".format(self.name, self.location)