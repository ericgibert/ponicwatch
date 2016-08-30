#!/bin/python3
"""
  A system is usually an hydroponic/acquaponic system for which one wamts to monitor various parameters
  like water temperature, pH, EC, etc..
  The atmosphere can be assimilated to a system too in order to montor air temperature and humidity for example.
"""

from model import Ponicwatch_table, Ponicwatch_Model

class System(Ponicwatch_table):

    _tb_system = (
        "system_id",  # INTEGER NOT NULL,
        "name",  # TEXT NOT NULL,
        "location",  # TEXT,
        "nb_plants",  # INTEGER NOT NULL DEFAULT(0),
        "sys_type"  # TEXT
    )

    def __init__(self, db, *args, **kwargs):
        Ponicwatch_table.__init__(self, db, "tb_system", System._tb_system, *args, **kwargs )

    @classmethod
    def all_keys(cls, db):
        return Ponicwatch_table.all_keys(db, "tb_system", "system_id")

if __name__ == "__main__":
    pw_db = Ponicwatch_Model("sqlite3", **{"database": "ponicwatch.db"})

    print(System.all_keys(pw_db))

    s = System(pw_db, id=1)
    print(s["system_id"], s)
    s = System(pw_db, system_id=2)
    print(s["system_id"], s)
    s = System(pw_db, name="Horizon 1")
    print("by 'id':", s["id"], s)

    try:
        s = System(pw_db)
        s.get_record()
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