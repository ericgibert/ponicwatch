#!/bin/python
"""
    Created by Eric Gibert on 29 Apr 2016

    model.py: the database model which can be used on both locally Sqlite3 and MySQL (or equivalent like MAriaDB) in the Cloud.
"""
import sys
import sqlite3

class Ponicwatch_Model():
    """
    Common 'interface' to be used to access the database layer without specific DBMS
    """
    def __init__(self, dbms, **server_params):
        self.server_params = server_params
        self.connect = sqlite3.connect
        # refer to: http://www.philvarner.com/test/ng-python3-db-api/
        # server_params = {'database': 'mydb',
        #          'host': 'localhost', 'port': '5432',
        #          'user': 'postgres', 'password': 'postgres'}

        # server_params = {'database': 'path to the file'}

    def get_connection(self):
        return self.connect(**self.server_params)

class User():
    def __init__(self, db):
        self.db = db
        self.user_id, self.login, self.email, self.authorization, self.password, self.name = None, None, None, None, None, None  # unknown user

    def get_user(self, login, password):
        """
        Fetch one record in tb_user matching the given parameters
        Convention: the controller itself must have the user_id = 1 and its login is 'ctrl'  --> secure access to add later
        :param name: tb_user.name
        :param password: tb_user.password --> to do: provide password encryption
        """
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                curs.execute("SELECT * from tb_user where login=? and password=?", (login, password))
                user_row = curs.fetchall()
                if len(user_row) == 1:
                    self.user_id, self.login, self.email, self.authorization, self.password, self.name = user_row[0]
            except:
                e = sys.exc_info()
                print("Error({0}): {1}".format(e.pgcode, e.pgerror))
            finally:
                curs.close()

    def __str__(self):
        return "{}".format(self.name)


if __name__ == "__main__":
    # test for the database on Sqlite3
    pw_db = Ponicwatch_Model("sqlite3", **{ "database" : "ponicwatch.db"})
    user = User(pw_db)
    user.get_user("ctrl", "passwd")
    print("Name: {}   user_id: {}".format(user, user.user_id))
    assert(user.user_id == 1)

    user.get_user("eric", "test")
    print("Name: {}   Email: {}".format(user, user.email))


