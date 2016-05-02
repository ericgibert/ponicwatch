#!/bin/python3
"""
  Test the integrity of the database models
"""
import unittest
from pw_db import Ponicwatch_db
from user import User
from ponic_system import Ponic_System
from switch import Switch
from sensor import Sensor


class Db_connection(unittest.TestCase):
    def test_connection(self):
        pw_db = Ponicwatch_db("sqlite3")
        print(pw_db)
        with pw_db.get_connection() as conn:
            curs = conn.cursor()
            try:
                curs.execute("select count(*) from tb_user")
                nb_rows = curs.fetchone()
                self.assertEqual(len(nb_rows), 1) # only one row returned by the select
                self.assertGreater(nb_rows[0], 0) # nb of users > 0
                print(nb_rows[0], "users in tb_users")
            finally:
                curs.close()

class Users(unittest.TestCase):
    def test_get_user(self):
        pw_db = Ponicwatch_db("sqlite3")
        user = User(pw_db)
        user.get_user("ctrl", "passwd")
        print("Name: {}  with user_id: {}".format(user, user["user_id"]))
        self.assertEqual(user["user_id"], 1)

        user = User(pw_db, "eric", "test")
        print("Name: {}   Email: {}".format(user, user["email"]))
        self.assertEqual(user["email"], "ericgibert@yahoo.fr")


class P_Systems(unittest.TestCase):
    def test_get_system(self):
        pw_db = Ponicwatch_db("sqlite3")
        psys = Ponic_System(pw_db)
        psys.get_system('Horizon 1')
        print("{} has the id: {}".format(psys, psys["system_id"]))
        self.assertEqual(psys["name"], 'Horizon 1')

        psys = Ponic_System(pw_db, 'Does Not Exist')
        self.assertEqual(psys["name"], None)
        print("'Does Not Exist' was not found...", psys["name"])


class Switchs(unittest.TestCase):
    def test_get_switch(self):
        """get by id first the use the name for testing get by name"""
        pw_db = Ponicwatch_db("sqlite3")
        switch1 = Switch(pw_db, id=1)
        self.assertEqual(switch1["switch_id"], 1)
        print("[{}] has the id: {}".format(switch1, switch1["switch_id"]))
        name = switch1["name"]
        switch1 = Switch(pw_db, name=name)
        self.assertEqual(switch1["switch_id"], 1)


class Sensors(unittest.TestCase):
    def test_get_sensor(self):
        """get by id first the use the name for testing get by name"""
        pw_db = Ponicwatch_db("sqlite3")
        sensor1 = Sensor(pw_db, id=1)
        self.assertEqual(sensor1["sensor_id"], 1)
        print("[{}] has the id: {}".format(sensor1, sensor1["sensor_id"]))
        name = sensor1["name"]
        sensor1 = Sensor(pw_db, name=name)
        self.assertEqual(sensor1["sensor_id"], 1)
        print("Last update on:", sensor1["updated_on"], type(sensor1["updated_on"]))

if __name__ == "__main__":
    # test for the database on Sqlite3
    unittest.main()