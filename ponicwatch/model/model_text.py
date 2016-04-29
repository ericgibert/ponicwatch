#!/bin/python3
"""
  Test the integrity of the database models
"""
import unittest
from pw_db import Ponicwatch_db
from user import User

class Db_connection(unittest.TestCase):
    def test_connection(self):
        pw_db = Ponicwatch_db("sqlite3", **{"database": "../ponicwatch.db"})
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
        pw_db = Ponicwatch_db("sqlite3", **{"database": "../ponicwatch.db"})
        print(pw_db)
        user = User(pw_db)
        user.get_user("ctrl", "passwd")
        print("Name: {}   user_id: {}".format(user, user.user_id))
        self.assertEqual(user.user_id, 1)

        user.get_user("eric", "test")
        print("Name: {}   Email: {}".format(user, user.email))
        self.assertEqual(user.email, "ericgibert@yahoo.fr")


if __name__ == "__main__":
    # test for the database on Sqlite3
    unittest.main()