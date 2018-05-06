#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Created by Eric Gibert on 06 April 2018

    Extract data from the database in the supersid format
"""
import argparse
from model.pw_db import Ponicwatch_Db
from pw_log import Ponicwatch_Log

__version__ = "1.20180406 Bangalore"
__author__ = 'Eric Gibert'
__license__ = 'MIT'

class ctrl:
    def __init__(self):
        self.name = 'Extraction'

def load_data(pwo_type, pwo):
    rows = log_table.get_all_records(page_len=0, columns="float_value, created_on", where_clause="log_type=? and object_id=?", args=[pwo_type, pwo])
    print(len(rows),"rows selected for", pwo_type, pwo)
    pwo_name = "{}_{}".format(pwo_type, pwo)
    pwo_list[pwo_name]=0.0
    for row in rows:
        timestamp = row[1].strftime("%Y-%m-%d %H:%M:%S")+".000000"
        if timestamp in data:
            data[timestamp].append( (pwo_name, row[0]) )
        else:
            data[timestamp] = [ (pwo_name, row[0]) ]



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sqlite", dest="dbfilename", help="Path of a Sqlite3 database.")  # type=exist_file, # required=False,
    parser.add_argument("-a", "--SENSORS",  dest="sensors", help="List of sensors", required=False, default="")
    parser.add_argument("-b", "--SWITCHES", dest="switches", help="List of switches", required=False,  default="")
    parser.add_argument("-f", "--from", dest="from", help="From time stamp", required=False,  default=None)
    parser.add_argument("-t", "--to", dest="to", help="To time stamp", required=False,  default=None)
    parser.add_argument('-v', '--version', action='version', version=__version__)
    args, unk = parser.parse_known_args()

    log_table = Ponicwatch_Log(controller=ctrl(), db=Ponicwatch_Db("sqlite3", {'database': args.dbfilename}), debug=3)

    data = {}  # dictionary key = timestamp, value = [ (pwo1, value1), (pwo2, value2), ... ]
    pwo_list = {}

    for pwo in args.sensors.split(","):
        load_data("SENSOR", pwo)

    with open("../Private/extraction.data", "wt") as fout:
        print("""# Site = RASPI
# Contact = 
# Longitude = 103.8
# Latitude = 1.367
#
# UTC_Offset = +08:00
# TimeZone = SGT
#
# UTC_StartTime = {} 00:00:00.00000
# LogInterval = 5
# LogType = raw
# MonitorID = SG1
# Frequencies = 19800,18200,16300
# Stations = {}""".format(min(data.keys())[:10], ','.join(pwo_list.keys())), file=fout)
        for t, vals in data.items():
            for v in vals:
                pwo_list[v[0]] = v[1]
            print(t+', ',", ".join([str(pv) for pv in pwo_list.values()]), file=fout)