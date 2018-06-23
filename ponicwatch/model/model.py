#!/bin/python
"""
    Created by Eric Gibert on 29 Apr 2016
    model.py: the database model which can be used on both locally Sqlite3 and MySQL (or equivalent like MAriaDB) in the Cloud.
"""
import json
from sqlite3 import InterfaceError
from datetime import datetime, timezone

class Ponicwatch_Table(dict):
    """associates a dictionary object to a table record"""
    INACTIVE = -1
    def __init__(self, db, META, *args, **kwargs):
        """
        Select one record from the given table
        META: dictionary providing the table's 'name', 'columns' and 'id' key
        """
        dict.__init__(self, *args, **kwargs)
        self.db = db
        self.table = META["table"]
        self.columns = META["columns"]
        self.id_column = META["id"]
        # is a record already requested? i.e one of the possible key argument is given as parameter
        if "id" in kwargs or self.id_column in kwargs:
            self.get_record(id=kwargs["id"] if "id" in kwargs else kwargs[self.id_column])
        elif "name" in kwargs:
            self.get_record(name=kwargs["name"])
        else:
            for col in self.columns:
                self[col] = None
            self["name"] = "<no record>"

    def execute_sql(self, sql, params=()):
        """Execute an SQL command on the cursor with exclusive access to the database"""
        nb_row = -1
        with self.db.exclusive_access:
            self.db.open()
            # print(sql, params)
            try:
                self.db.curs.execute(sql, params)
                self.db.conn.commit()
                nb_row = self.db.curs.rowcount
            except InterfaceError as err:
                print('*'*30, err)
                print(sql)
                print(params)
            finally:
                self.db.close()
        return nb_row


    def fetch(self, sql, params=[], only_one=False):
        with self.db.exclusive_access:
            rows= None
            self.db.open()
            try:
                self.db.curs.execute(sql, params)
                rows = self.db.curs.fetchone() if only_one else self.db.curs.fetchall()
            except InterfaceError as err:
                print('*'*30, err)
                print(sql)
                print(params)
            finally:
                self.db.close()
        return rows

    def get_record(self, id=None, name=None):
        """select on record form the table"""
        with self.db.exclusive_access:
            self.db.open()
            try:
                if type(id) is int:
                    self.db.curs.execute("SELECT * FROM {0} WHERE {1}=?".format(self.table, self.id_column), (id,))
                elif type(name) is str:
                    self.db.curs.execute("SELECT * FROM {0} WHERE name=?".format(self.table), (name,))
                else:
                    raise ValueError("Missing or incorrect argument: id or name")
                rows = self.db.curs.fetchall()
                if len(rows) == 1:
                    r = rows[0]
                    for col in r.keys():
                        self[col] = r[col]
                    self["id"] = r[self.id_column]
                elif len(rows) == 0: # unknown key
                    raise KeyError("Unkown record key on id/name: " + str(name or id))
                else: # not a key: more than one record found ?1?
                    raise KeyError("Too many records found ?!? Not a key on id/name: " + str(name or id))
            finally:
                self.db.close()
        # convert the JSON init string to a python dictionary
        try:
            self.init_dict = json.loads(self["init"])
        except KeyError:
            # print("Warning ---> no init field for", self)
            self.init_dict = {}
        except:  # json.JSONDecodeError:
            print("Warning: init is not a JSON string for", self)
            print("init=", self["init"])


    def get_all_records(self, page_len=20, from_page=0, where_clause=None, order_by=None, args=[], columns='*'):
        """
        Return a list of all the table records starting from the right page
            page_len: number of rows in one page. If given as 0 then no LIMIT set in the SELECT statement 
        """
        sql = "SELECT {} FROM {}".format(columns, self.table)
        if where_clause:
            sql += " WHERE " + where_clause
        if order_by:
            sql += " ORDER BY " + order_by
        if page_len:
            sql += " LIMIT {} OFFSET {}".format(page_len, from_page * page_len)
        with self.db.exclusive_access:
            self.db.open()
            try:
                self.db.curs.execute(sql, args)
                rows = self.db.curs.fetchall()
            except InterfaceError as err:
                print('*'*30, err)
                print(sql)
            finally:
                self.db.close()
        return rows

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
        # update_on timestamp managenemt
        if 'updated_on' in self.columns and 'updated_on' not in kwargs:
            col_value.append( ('updated_on', datetime.now(timezone.utc)) )
        # SQL statement build and execution
        if col_value:
            sql = "UPDATE {0} SET {1} WHERE {2}=?".format(self.table,
                                                          ",".join([c+"=?" for c, v in col_value]),
                                                          self.id_column)
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
            # self.get_record(id=self.db.curs.lastrowid)  # reload data after the insert - NO NEED, AS ONLY LOG INSERTS

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


