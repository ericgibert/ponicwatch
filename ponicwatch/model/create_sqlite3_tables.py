"""
Create the tables intp an empty Sqlite3 table.

SQL statemebts copied from test database
"""
import sqlite3

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
"""
}

def create_tables(db_path):
    """Loop thru all table and execute them"""
    with sqlite3.connect(db_path) as conn:
        curs = conn.cursor()
        for table, sql in sql_statements.items():
            curs.execute(sql)
        conn.commit()
