#!/bin/python3
"""
    Created by Eric Gibert on 12 May 2016

    Controller
"""
import argparse
import os.path
from model.pw_db import Ponicwatch_db
from model.pw_log import Ponicwatch_log
from model.user import User

DEBUG = True  # activate theDebug mode or not

class Controller(object):

    def __init__(self, db):
        self.db = db
        # finding the Controller User entry
        self.user = User(self.db, "ctrl", "passwd")
        self.name = self.user["name"]
        # opening the LOG
        self.log = Ponicwatch_log(self.db, debug=DEBUG)
        self.log["controller_name"] = self.name

    def run(self):
        self.log.add_info("Controller is now running")


def exist_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.isfile(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sqlite", dest="dbfilename",  type=exist_file, # required=False,
                        help="Path of a Sqlite3 database.")
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()

    if args.dbfilename:
        db = Ponicwatch_db("sqlite3", [args.dbfilename])
        ctrl = Controller(db)
        ctrl.run()
    else:
        print("currently: -s dbfilename is mandatory")
