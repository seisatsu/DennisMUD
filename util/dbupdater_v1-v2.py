#######################
# Dennis MUD          #
# dbupdater_v1-v2.py  #
# Copyright 2020-2022 #
# Sei Satzparad       #
#######################

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

from os import path
import sys

from tinydb import Query

try:
    from lib import database
except:
    print("Can't find DatabaseManager. You should move this script to the Dennis root directory.")
    sys.exit(1)


UPDATE_TO_VERSION = 2


# DatabaseManager will expect a logger, so we'll give it this stump.
class Log:
    """Stand-in for Twisted's logger.
    """
    def debug(self, msg, **kwargs):
        print("[cli#debug]", msg.format(**kwargs))

    def info(self, msg, **kwargs):
        print("[cli#info]", msg.format(**kwargs))

    def warn(self, msg, **kwargs):
        print("[cli#warn]", msg.format(**kwargs))

    def error(self, msg, **kwargs):
        print("[cli#error]", msg.format(**kwargs))

    def critical(self, msg, **kwargs):
        print("[cli#critical]", msg.format(**kwargs))


def dbupdate_v1_to_v2(dbman):
    """Database Updater for v1 to v2.

    This update adds an empty "entrances" field to every room, and then combs through the exits
    of every room in the world to populate the entrance records.

    This is needed for the `list entrances` command to not take several seconds on larger worlds.
    """
    # Counters and variables.
    ri = 0
    exi = 0
    eni = 0
    rooms = dbman.rooms.all()
    q = Query()

    # Perform the updates.
    if len(rooms):
        # Add an empty entrance field to every room.
        for thisroom in rooms:
            thisroom["entrances"] = []
            dbman.upsert_room(thisroom)
        print("Added an empty entrance field to {0} rooms.".format(len(rooms)))

        # Process the exits of every room to populate the corresponding entrance records.
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

        # We are finished, so update the database version record.
        info_record = dbman._info.all()[0]
        info_record["version"] = UPDATE_TO_VERSION
        dbman._info.upsert(info_record, q.version == dbman._UPDATE_FROM_VERSION)

    # The database is actually empty somehow. Do nothing.
    else:
        print("No rooms.")


def main():
    """Main Program
    """
    print("Dennis 2D Database Updater v1 -> v2")

    # Check command line arguments, and give help if needed.
    if len(sys.argv) != 2 or sys.argv[1] in ["help", "-h", "--help", "-help", "?", "-?"]:
        print("This updater adds entrance records to rooms for the `list entrances` command.")
        print("Usage: {0} <database>".format(sys.argv[0]))
        return 0

    # Make sure the database file exists.
    if not path.exists(sys.argv[1]):
        print("Database file does not exist: {0}".format(sys.argv[1]))
        return 1

    # Start up DatabaseManager and tell it we're accepting a v1 database for migration.
    dbman = database.DatabaseManager(sys.argv[1], log=Log())
    dbman._UPDATE_FROM_VERSION = 1
    sres = dbman._startup()
    if not sres:
        return 1

    # Run the updates for this migration.
    dbupdate_v1_to_v2(dbman)

    # Finished.
    print("Successfully updated database from v1 to v2: {0}".format(sys.argv[1]))
    dbman._unlock()


if __name__ == "__main__":
    sys.exit(main())
