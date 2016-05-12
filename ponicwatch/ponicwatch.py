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

class Controller(object):

    def __init__(self, db):
        self.db = db
        self.user = User(db, "ctrl", "passwd")
        print(self.user)

    def run(self):
        print("running")


def exist_file(x):
    """
    'Type' for argparse - checks that file exists but does not open.
    """
    if not os.path.isfile(x):
        raise argparse.ArgumentError("{0} does not exist".format(x))
    return x

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sqlite", dest="dbfilename", required=False, type=exist_file,
                        help="Path of a Sqlite3 database.")
    # parser.add_argument('config_file', nargs='?', default='')
    args, unk = parser.parse_known_args()

    if args.dbfilename:
        db = Ponicwatch_db("sqlite3", [args.dbfilename])
        ctrl = Controller(db)
        ctrl.run()
    else:
        print("currently: -s dbfilename is mandatory")
