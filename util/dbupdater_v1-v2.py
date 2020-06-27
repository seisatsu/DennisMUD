######################
# Dennis MUD         #
# dbupdater_v1-v2.py #
# Copyright 2020     #
# Michael D. Reiley  #
######################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

# This is the Dennis 2D Database Updater for v1 -> v2 migration.
# To use it, copy it into your main Dennis directory and run it
# with the database filename as its only argument. This updater
# adds entrance records to rooms.

import json
from os import path
import sys

from tinydb import Query

try:
    import database
except:
    print("Can't find DatabaseManager. You should move this script to the Dennis root directory.")
    sys.exit(1)


if len(sys.argv) != 2 or sys.argv[1] in ["help", "-h", "--help", "-help", "?", "-?"]:
    print("Dennis 2D Database Updater v1 -> v2")
    print("This updater adds entrance records to rooms.")
    print("Usage: {0} <database>".format(sys.argv[0]))
    sys.exit(0)


class Log:
    """Stand-in for Twisted's logger.
    """
    def debug(self, msg, **kwargs):
        print("[debug]", msg.format(**kwargs))

    def info(self, msg, **kwargs):
        print(msg.format(**kwargs))

    def warn(self, msg, **kwargs):
        print("[warn]", msg.format(**kwargs))

    def error(self, msg, **kwargs):
        print("[error]", msg.format(**kwargs))

    def critical(self, msg, **kwargs):
        print("[critical]", msg.format(**kwargs))


if not path.exists(sys.argv[1]):
    print("Database file does not exist: {0}".format(sys.argv[1]))
    sys.exit(1)

# Start up DatabaseManager and tell it we're accepting a v1 database.
dbman = database.DatabaseManager(sys.argv[1], Log())
dbman._UPDATE_FROM_VERSION = 1
sres = dbman._startup()
if not sres:
    sys.exit(1)

# Perform updates.
ri = 0
exi = 0
eni = 0
rooms = dbman.rooms.all()
q = Query()

if len(rooms):
    for thisroom in rooms:
        thisroom["entrances"] = []
        dbman.upsert_room(thisroom)
    print("Added an empty entrance field to {0} rooms.".format(len(rooms)))

    for thisroom in rooms:
        ri += 1
        for ex in thisroom["exits"]:
            exi += 1
            destroom = dbman.room_by_id(ex["dest"])
            if thisroom["id"] not in destroom["entrances"]:
                eni += 1
                destroom["entrances"].append(thisroom["id"])
                dbman.upsert_room(destroom)
    print("Processed {0} exits in {1} rooms and added {2} entrance records.".format(exi, ri, eni))

    info_record = dbman._info.all()[0]
    info_record["version"] = database.DB_VERSION
    dbman._info.upsert(info_record, q.version == dbman._UPDATE_FROM_VERSION)

else:
    print("No rooms.")

print("Successfully updated database from v1 to v2: {0}".format(sys.argv[1]))
dbman._unlock()
