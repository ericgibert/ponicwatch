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
        # is a record already requested? i.e one of the possible key argument is given as parameter
        if {"id", "name", "system_id"} & set(kwargs):
            self.get_system(**kwargs)
        else:
            for col in System._tb_system:
                self[col] = None
            self["name"] = "<no system>"

    def get_system(self, system_id=None, id=None, name=None):
        """get on record form tb_system"""
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                if type(name) is str:
                    curs.execute("SELECT * from tb_system where name=?", (name,))
                elif type(system_id or id) is int:
                    curs.execute("SELECT * from tb_system where system_id=?", (system_id or id,))
                else:
                    raise ValueError("Missing or incorrect argument: id or system_id or name")
                switch_row = curs.fetchall()
                if len(switch_row) == 1:
                    for idx, col in enumerate(System._tb_system):
                        self[col] = switch_row[0][idx]
                elif len(switch_row) == 0: # unknown key
                    raise KeyError("Unkown record key on id/system_id/name: " + str(name or system_id or id))
                else: # not a key: more than one record found ?1?
                    raise KeyError("Too many records found ?!? Not a key on id/system_id/name: " + str(name or system_id or id))
            finally:
                curs.close()

    def __str__(self):
        return self["name"]

if __name__ == "__main__":
    from model import Ponicwatch_Model
    pw_db = Ponicwatch_Model("sqlite3", **{"database": "ponicwatch.db"})
    s = System(pw_db, id=1)
    print(s["system_id"], s)
    s = System(pw_db, system_id=2)
    print(s["system_id"], s)
    s = System(pw_db, name="Horizon 1")
    print(s["system_id"], s)

    try:
        s = System(pw_db)
        s.get_system()
        print("No arguments:", s["system_id"], s)
    except ValueError as err:
        print("Expected ValueError:", err, sep="\n")

    try:
        s = System(pw_db, toilet="paper")
        print("Useless argument:", s["system_id"], s)
    except TypeError as err:
        print("Expected TypeError:", err, sep="\n")

    try:
        s = System(pw_db, system_id="deux")
        print("Incorrect arguments:", s["system_id"], s)
    except ValueError as err:
        print("Expected ValueError:", err, sep="\n")

    try:
        s = System(pw_db, system_id=999999)
        print("Unkown record id:", s["system_id"], s)
    except KeyError as err:
        print(err, sep="\n")