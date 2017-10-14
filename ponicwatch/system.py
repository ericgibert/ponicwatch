#!/bin/python3
"""
  A system is usually an hydroponic/acquaponic system for which one wamts to monitor various parameters
  like water temperature, pH, EC, etc..
  The atmosphere can be assimilated to a system too in order to montor air temperature and humidity for example.
"""

from model.model import Ponicwatch_Table

class System(Ponicwatch_Table):
    """
    - name: to identify the system easily withion an area
    - location: where is the system installed
    - sys_type: NFT, aeroponic, Ebb and Flow, etc
    - nb_plants:  *important* number of plants is necessary to track the timing of plantations --> to do list
    """
    META = {"table": "tb_system",
            "id": "system_id",
            "columns": (
                        "system_id",  # INTEGER NOT NULL,
                        "name",  # TEXT NOT NULL,
                        "location",  # TEXT,
                        "nb_plants",  # INTEGER NOT NULL DEFAULT(0),
                        "sys_type"  # TEXT
                       )
            }

    def __init__(self, controller, db=None, *args, **kwargs):
        super().__init__(db or controller.db, System.META, *args, **kwargs)

    def __str__(self):
        return "{} ({})".format(self["name"], self["location"])

    @classmethod
    def all_keys(cls, db):
        return super().all_keys(db, System.META)

if __name__ == "__main__":
    from model.pw_db import Ponicwatch_Db
    pw_db = Ponicwatch_Db("sqlite3", {"database": "ponicwatch.db"})

    systems = System.all_keys(pw_db)
    print("All System ids:", systems)

    horizon1 = System(pw_db, name="Horizon 1")
    print(horizon1["id"], horizon1)

    system_1 = System(pw_db, id=1)
    print(system_1["id"], system_1)

    system_2 = System(pw_db, system_id=2)
    print(system_2["id"], system_2, "has", system_2["nb_plants"])
    system_2.update(nb_plants=system_2["nb_plants"]+1)
    print("After update:", system_2["nb_plants"])

    try:
        system_3 = System(pw_db, system_id=99999)
        print(system_3["id"], system_3)
    except KeyError as err:
        print("Negative test is OK:", err)