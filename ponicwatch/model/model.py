#!/bin/python
"""
    Created by Eric Gibert on 29 Apr 2016
    model.py: the database model which can be used on both locally Sqlite3 and MySQL (or equivalent like MAriaDB) in the Cloud.
"""
import json
from sqlite3 import InterfaceError
class Ponicwatch_Table(dict):
    """associates a dictionary object to a table record"""
    def __init__(self, db, META, *args, **kwargs):
        """
        Select one record from the given table
        META: dictionary providing the table's 'name', 'columns' and 'id' key
        """
        dict.__init__(self, *args, **kwargs)
        self.db = db
        self.table = META["table"]
        self.columns = META["columns"]
        self.id = META["id"]
        # is a record already requested? i.e one of the possible key argument is given as parameter
        if "id" in kwargs or self.id in kwargs:
            self.get_record(id=kwargs["id"] if "id" in kwargs else kwargs[self.id])
        elif "name" in kwargs:
            self.get_record(name=kwargs["name"])
        else:
            for col in self.columns:
                self[col] = None
            self["name"] = "<no record>"

    def execute_sql(self, sql, params):
        """Execute an SQL command on the cursor with exclusive access to the database"""
        with self.db.exclusive_access:
            self.db.open()
            try:
                self.db.curs.execute(sql, params)
                self.db.conn.commit()
            except InterfaceError as err:
                print('*'*30, err)
                print(sql)
                print(params)
            finally:
                self.db.close()

    def get_record(self, id=None, name=None):
        """select on record form the table"""
        with self.db.exclusive_access:
            self.db.open()
            try:
                if type(id) is int:
                    self.db.curs.execute("SELECT * FROM {0} WHERE {1}=?".format(self.table, self.id), (id,))
                elif type(name) is str:
                    self.db.curs.execute("SELECT * FROM {0} WHERE name=?".format(self.table), (name,))
                else:
                    raise ValueError("Missing or incorrect argument: id or name")
                rows = self.db.curs.fetchall()
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
                if "init" in self:
                    try:
                        self.init_dict = json.loads(self["init"]) if self["init"] else {}
                    except : #json.JSONDecodeError:
                        print("Warning: init is not a JSON string for", self)
                        print("init=", self["init"])
                else:
                    # print("---> no init field for", self)
                    try:
                        print("-->", self["init"])
                    except:
                        pass
                self.db.close()

    def __str__(self):
        return self["name"]

    def update(self, **kwargs):
        """update the fields given as parameters with their values using the 'kwargs' dictionary"""
        col_value = [] # list of tuple col=value to update
        for col, val in kwargs.items():
            if col in self.columns:
                col_value.append( (col, val) )
            else:
                raise KeyError(col, ": column cannot be updated. Is it properly spelled?")
        if col_value:
            sql = "UPDATE {0} SET {1} WHERE {2}=?".format(self.table,
                                                          ",".join([c+"=?" for c, v in col_value]),
                                                          self.id)
            # print("sql =", sql)
            self.execute_sql(sql, [v for c, v in col_value] + [self["id"]])
            self.get_record(id=self["id"]) # reload data after the update

    def insert(self, **kwargs):
        """INSERT a record in the table"""
        col_value = []  # list of tuple col=value to insert
        for col, val in kwargs.items():
            if col in self.columns:
                col_value.append((col, val))
            else:
                raise KeyError(col, ": column cannot be inserted. Is it properly spelled?")
        if col_value:
            sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(self.table,
                                                                ",".join([c for c, v in col_value]),
                                                                ",".join("?" * len(col_value)))
            self.execute_sql(sql, [v for c, v in col_value])
            self.get_record(id=self.db.curs.lastrowid)  # reload data after the update

    @classmethod
    def all_keys(cls, db, META):
        """return all the keys found in the table"""
        try:
            db.open()
            db.curs.execute("SELECT {0} from {1}".format(META["id"], META["table"]))
            rows = db.curs.fetchall()
        finally:
            db.close()
        return [r[0] for r in rows]

    @classmethod
    def get_field_value(cls, db, META, id, field):
        """return the unique value from the table.field matching the id"""
        try:
            db.open()
            db.curs.execute("SELECT {0} from {1} where {2}={3}".format(field, META["table"], META["id"], id))
            row = db.curs.fetchone()
        finally:
            db.close()
        return row


