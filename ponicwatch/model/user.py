#!/bin/python3
"""
    Model for the table tb_user.
    Created by Eric Gibert on 29 Apr 2016

    Users authorized to connect to the database.

    Convention: the controller itself must have the user_id = 1 and its login is 'ctrl'  --> secure access to add later
                the controller's name is used as an identifian in the tb_log table: it must be unique across all the supervised installations

    'login' and 'password' must be unique as they are used to query the table.
"""

class User(dict):

    _tb_user = (
        "user_id", # INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        "login", # TEXT NOT NULL,
        "email", # TEXT NOT NULL,
        "authorization", # INTEGER NOT NULL DEFAULT (0),
        "password", # TEXT,
        "name", # TEXT
    )

    def __init__(self, db, login=None, password=None, *args,**kwargs):
        dict.__init__(self, *args,**kwargs)
        self.db = db
        for col in User._tb_user:
            self[col] = None
        if login and password:
            self.get_user(login, password)

    def get_user(self, login, password):
        """
        Fetch one record in tb_user matching the given parameters
        :param name: tb_user.name
        :param password: tb_user.password --> to do: provide password encryption
        """
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                curs.execute("SELECT * from tb_user where login=? and password=?", (login, password))
                user_row = curs.fetchall()
                if len(user_row) == 1:
                    for idx, col in enumerate(User._tb_user):
                        self[col] = user_row[0][idx]
            finally:
                curs.close()

    def __str__(self):
        """
        Returns the user's name.
        Very important for the controller as its name is used to identify the log entries' origin i.e. must be unique.
        """
        return "{}".format(self["name"])