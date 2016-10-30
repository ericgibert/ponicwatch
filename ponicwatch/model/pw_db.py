#!/bin/python3
"""
    Created by Eric Gibert on 29 Apr 2016

    pw_db.py: the database connection parameters which can be used on both locally Sqlite3 and MySQL (or equivalent like MariaDB) in the Cloud.
"""
import os
# import atexit
import sqlite3

class Ponicwatch_Db():
    """
    Common 'interface' to be used to access the database layer with a specific DBMS
    """
    def __init__(self, dbms, server_params, clean_tables=False):
        """Connects to a database and create a cursor. Ensure the db closing at exit"""
        assert(dbms in ["sqlite3", "mysql"])
        assert(type(server_params) is dict)
        if dbms == "sqlite3" and "database" in server_params:
            # server_params = {'database': 'path to the file', "detect_types": sqlite3.PARSE_DECLTYPES}
            # to allow datetime conversion for timestamps
            if "detect_types" not in server_params:
                server_params["detect_types"] = sqlite3.PARSE_DECLTYPES
            if not os.path.isfile(server_params["database"]):
                self.create_tables(server_params["database"])
            self.connect = sqlite3.connect
            self.allow_close = True
        else:
            # refer to: http://www.philvarner.com/test/ng-python3-db-api/
            # server_params = {'database': 'mydb',
            #          'host': 'localhost', 'port': '5432',
            #          'user': 'postgres', 'password': 'postgres'}
            pass
        self.dbms = dbms
        self.server_params = server_params
        self.is_open = False
        if clean_tables:
            self.clean()

    def open(self):
        self.conn = self.connect(**self.server_params)
        self.curs = self.conn.cursor()
        self.is_open = True

    def close(self):
        if self.allow_close:
            self.curs.close()
            self.conn.close()
            self.is_open = False

    def clean(self):
        self.open()
        try:
            for sql in ("delete from tb_log",):
                self.curs.execute(sql)
            self.conn.commit()
        except sqlite3.InterfaceError as err:
            print('*' * 30, err)
        finally:
            self.close()

    def __str__(self):
        return "{} on {}".format(self.server_params["database"],self.dbms)

    def synchro_to_cloud(self):
        """Synchronize selected tables from local Sqlite3 db to MySQL db in the Cloud"""
        pass


    def create_tables(self, db_path):
        """Loop thru all table and execute them"""
        with sqlite3.connect(db_path) as conn:
            curs = conn.cursor()
            for table, sql in sql_statements.items():
                curs.execute(sql)
            conn.commit()


sql_statements = {

'tb_log': """CREATE TABLE tb_log (
"log_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "controller_name" TEXT NOT NULL,
    "log_type" TEXT NOT NULL,
    "object_id" INTEGER NOT NULL,
    "system_name" TEXT NOT NULL,
    "float_value" REAL NOT NULL DEFAULT (0.0),
    "text_value" TEXT,
    "created_on" TIMESTAMP NOT NULL
)""",

'tb_sensor': """CREATE TABLE tb_sensor (
    "sensor_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "mode" INTEGER NOT NULL DEFAULT (0),
    "hardware" TEXT NOT NULL
  , "timer" TEXT,
    "read_value" FLOAT NOT NULL DEFAULT (0.0),
    "calculated_value" REAL NOT NULL DEFAULT (0.0),
    "timestamp_value" TIMESTAMP,
    "updated_on" TIMESTAMP,
    "synchro_on" TIMESTAMP
)""",
'tb_switch':    """CREATE TABLE tb_switch (
    "switch_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "mode" INTEGER NOT NULL DEFAULT (0),
    "hardware" TEXT NOT NULL,
    "timer" TEXT NOT NULL,
    "value" INTEGER NOT NULL DEFAULT (0),
    "timer_interval" INTEGER NOT NULL DEFAULT (15),
    "updated_on" TIMESTAMP,
    "synchro_on" TIMESTAMP
)
""",
'tb_system':    """CREATE TABLE tb_system (
    "system_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "location" TEXT,
    "nb_plants" INTEGER NOT NULL DEFAULT (0),
    "sys_type" TEXT
)""",

'tb_user':    """CREATE TABLE tb_user (
    "user_id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "login" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "authorization" INTEGER NOT NULL DEFAULT (0),
    "password" TEXT,
    "name" TEXT
)
""",
'tb_link': """CREATE TABLE tb_link (
    "system_id" INTEGER NOT NULL,
    "sensor_id" INTEGER,
    "switch_id" INTEGER,
    "hardware_id" INTEGER,
    "order_for_creation" INTEGER  NOT NULL  DEFAULT (0),
    "interrupt_id" INTEGER)
""",
 'tb_interrupt': """CREATE TABLE tb_interrupt (
    "interrupt_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "hardware" TEXT NOT NULL,
    "init" TEXT,
    "threshold" INTEGER NOT NULL DEFAULT (0),
    "updated_on" TIMESTAMP,
    "synchro_on" TIMESTAMP
)
    """
}


if __name__ == "__main__":
    db = Ponicwatch_Db("sqlite3", {'database': "test_to_delete.db"})
