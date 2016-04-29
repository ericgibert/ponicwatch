#!/bin/python
"""
    Created by Eric Gibert on 29 Apr 2016

    model.py: the database model which can be used on both locally Sqlite3 and MySQL (or equivalent like MAriaDB) in the Cloud.
"""
import sqlite3

class Ponicwatch_db():
    """
    Common 'interface' to be used to access the database layer without specific DBMS
    """
    def __init__(self, dbms, **server_params):
        self.server_params = server_params
        self.connect = sqlite3.connect if dbms == "sqlite3" else None
        # refer to: http://www.philvarner.com/test/ng-python3-db-api/
        # server_params = {'database': 'mydb',
        #          'host': 'localhost', 'port': '5432',
        #          'user': 'postgres', 'password': 'postgres'}

        # server_params = {'database': 'path to the file'}

    def get_connection(self):
        return self.connect(**self.server_params)




