#!/bin/python3
"""
    Model for the table tb_user.
    Created by Eric Gibert on 29 Apr 2016

    Users authorized to connect to the database.

    Convention: the controller itself must have the user_id = 1 and its login is 'ctrl'  --> secure access to add later
                the controller's name is used as an identifian in the tb_log table: it must be unique across all the supervised installations

    'login' and 'password' must be unique as they are used to query the table.
"""
from model.model import Ponicwatch_Table

class User(Ponicwatch_Table):
    """Access the tb_user table to fetch a user's information"""
    META={"table": "tb_user",
          "id": "user_id",
          "columns": (
                    "user_id",          # INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    "login",            # TEXT NOT NULL,
                    "email",            # TEXT NOT NULL,
                    "authorization",    # INTEGER NOT NULL DEFAULT (0),
                    "password",         # TEXT,
                    "name"              # TEXT
                    )
          }

    def __init__(self, controller=None, db=None, *args, **kwargs):
        super().__init__(db or controller.db, User.META, *args, **kwargs)

    def get_user(self, login, password):
        """
        Fetch one record in tb_user matching the given parameters
        Convention: the controller itself must have the user_id = 1 and its login is 'ctrl'  --> secure access to add later
        :param name: tb_user.name
        :param password: tb_user.password --> to do: provide password encryption
        """
        self.db.open()
        try:
            self.db.curs.execute("SELECT user_id from tb_user where login=? and password=?", (login, password))
            user_row = self.db.curs.fetchall()
        finally:
            self.db.close()
        if len(user_row) == 1:
            self.get_record(id=user_row[0][0])
        else:
            self["id"] = None

if __name__ == "__main__":
    from model.pw_db import Ponicwatch_Db
    # test for the database on Sqlite3
    pw_db = Ponicwatch_Db("sqlite3", {"database": "local_ponicwatch.db"})
    user = User(db=pw_db, id=1)
    #user.get_user(id=1)
    print("1) Name: {}   user {}: {} {}".format(user, user["id"], user["login"], user["password"]))

    new_user = User(db=pw_db, id=user["id"])
    print("2) Name: {}   user_id: {}".format(new_user, new_user["id"]))

    new_user = User(db=pw_db)
    new_user.insert(login="new", email="new@new", authorization=0, password="qwertyuiop", name="New User")
    # print("3) Name: {}   user_id: {}".format(new_user, new_user["id"]))
