#!/bin/python3
"""
    Created by Eric Gibert on 29 Apr 2016

    pw_db.py: the database connection parameters which can be used on both locally Sqlite3 and MySQL (or equivalent like MariaDB) in the Cloud.
"""
import os
import atexit
import sqlite3
from create_sqlite3_tables import create_tables

class Ponicwatch_Db():
    """
    Common 'interface' to be used to access the database layer with a specific DBMS
    """
    def __init__(self, dbms, server_params):
        """Connects to a database and create a cursor. Ensure the db closing at exit"""
        assert (dbms in ["sqlite3", "mysql"])
        if dbms == "sqlite3" and "database" in server_params:
            # server_params = {'database': 'path to the file', "detect_types": sqlite3.PARSE_DECLTYPES}
            # to allow datetime conversion for timestamps
            if "detect_types" not in server_params:
                server_params["detect_types"] = sqlite3.PARSE_DECLTYPES
            if not os.path.isfile(server_params["database"]):
                create_tables(server_params["database"])
            self.connect = sqlite3.connect
        else:
            # refer to: http://www.philvarner.com/test/ng-python3-db-api/
            # server_params = {'database': 'mydb',
            #          'host': 'localhost', 'port': '5432',
            #          'user': 'postgres', 'password': 'postgres'}
            pass

        _conn = self.connect(**server_params)
        self.conn = _conn
        _curs = self.conn.cursor()
        self.curs = _curs

        @atexit.register
        def close():
            _curs.close()
            _conn.close()

    def __str__(self):
        return "{} on {}".format(self.server_params["database"],self.dbms)

    def synchro_to_cloud(self):
        """Synchronize selected tables from local Sqlite3 db to MySQL db in the Cloud"""
        pass




