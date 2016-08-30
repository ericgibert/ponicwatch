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

class Ponicwatch_table(dict):
    """associates a dictionary to a table record"""
    def __init__(self, db, table, columns, *args,**kwargs):
        """Select one record from the given table"""
        dict.__init__(self, *args, **kwargs)
        self.db = db
        self.table = table
        self.columns = columns
        # look for the record id as a column's name ending with '_id'
        for col in columns:
            if col.endswith("_id"):
                self.id = col
                break
        # is a record already requested? i.e one of the possible key argument is given as parameter
        if "name" in kwargs:
            self.get_record(name=kwargs["name"])
        elif "id" in kwargs:
            self.get_record(id=kwargs["id"])
        elif self.id in kwargs:
            self.get_record(id=kwargs[self.id])
        else:
            for col in self.columns:
                self[col] = None
            self["name"] = "<no record>"

    def get_record(self, id=None, name=None):
        """get on record form the table"""
        with self.db.get_connection() as conn:
            curs = conn.cursor()
            try:
                if type(name) is str:
                    curs.execute("SELECT * from %s where name=?" % self.table, (name,))
                elif type(id) is int:
                    curs.execute("SELECT * from %s where system_id=?" % self.table, (id,))
                else:
                    raise ValueError("Missing or incorrect argument: id or name")
                rows = curs.fetchall()
                if len(rows) == 1:
                    for idx, col in enumerate(self.columns):
                        self[col] = rows[0][idx]
                        if col == self.id:
                            self["id"] = rows[0][idx]
                elif len(rows) == 0: # unknown key
                    raise KeyError("Unkown record key on id/name: " + str(name or id))
                else: # not a key: more than one record found ?1?
                    raise KeyError("Too many records found ?!? Not a key on id/name: " + str(name or id))
            finally:
                curs.close()

    def __str__(self):
        return self["name"]

    @classmethod
    def all_keys(cls, db, table, id):
        """return all the keys found in the table"""
        rows = []
        with db.get_connection() as conn:
            curs = conn.cursor()
            try:
                curs.execute("SELECT %s from %s" % (id, table))
                rows = curs.fetchall()
            finally:
                curs.close()
        return [r[0] for r in rows]


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


