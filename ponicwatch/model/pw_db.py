#!/bin/python3
"""
    Created by Eric Gibert on 29 Apr 2016

    pw_db.py: the database connection parameters which can be used on both locally Sqlite3 and MySQL (or equivalent like MariaDB) in the Cloud.
"""
import os
import sqlite3
from model.create_sqlite3_tables import create_tables

class Ponicwatch_db(object):
    """
    Common 'interface' to be used to access the database layer without specific DBMS
    """
    def __init__(self, dbms, params=[]):
        """Either sqlite3 or mySQL connection"""
        assert(dbms in ["sqlite3", "mysql"])
        self.dbms = dbms
        if dbms == "sqlite3":
            # params[0]: full path to the Sqlite3 database
            if not os.path.isfile(params[0]):
                create_tables(params[0])

            self.server_params = {"database": params[0], "detect_types": sqlite3.PARSE_DECLTYPES} # to allow datetime converion for timestamps
            self.connect = sqlite3.connect
        elif dbms == "mysql":
            pass
        else:
            raise ValueError

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




