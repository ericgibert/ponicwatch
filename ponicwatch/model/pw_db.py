#!/bin/python
"""
    Created by Eric Gibert on 29 Apr 2016

    pw_db.py: the database connection parameters which can be used on both locally Sqlite3 and MySQL (or equivalent like MariaDB) in the Cloud.
"""
import sqlite3

class Ponicwatch_db(object):
    """
    Common 'interface' to be used to access the database layer without specific DBMS
    """
    def __init__(self, dbms, **server_params):
        self.server_params = server_params
        self.dbms = dbms
        self.connect = sqlite3.connect if dbms == "sqlite3" else None

        # refer to: http://www.philvarner.com/test/ng-python3-db-api/
        # server_params = {'database': 'mydb',
        #          'host': 'localhost', 'port': 'leave default',
        #          'user': 'machin', 'password': 'bidule'}

        # refer tp: https://docs.python.org/3.4/library/sqlite3.html
        # server_params = {'database': 'path to the file'} for Sqlite3

    def get_connection(self):
        return self.connect(**self.server_params)

    def __str__(self):
        return "{} on {}".format(self.server_params["database"],self.dbms)

    def synchro_to_cloud(self):
        """Synchronize selected tables from local Sqlite3 db to MySQL db in the Cloud"""
        pass




