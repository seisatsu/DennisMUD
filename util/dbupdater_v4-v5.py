#######################
# Dennis MUD          #
# dbupdater_v4-v5.py  #
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

# This is the Dennis 2D Database Updater for v4 -> v5 migration.
# To use it, copy it into your main Dennis directory and run it
# with the database filename as its only argument. This updater
# adds an entrance action field to all exits.

from os import path
import sys

from tinydb import Query

try:
    from lib import database
except:
    print("Can't find DatabaseManager. You should move this script to the Dennis root directory.")
    sys.exit(1)


UPDATE_TO_VERSION = 5


# DatabaseManager will expect a logger, so we'll give it this stump.
class Log:
    """Stand-in for Twisted's logger.
    """
    def debug(self, msg, **kwargs):
        print("[dbupdater#debug]", msg.format(**kwargs))

    def info(self, msg, **kwargs):
        print("[dbupdater#info]", msg.format(**kwargs))

    def warn(self, msg, **kwargs):
        print("[dbupdater#warn]", msg.format(**kwargs))

    def error(self, msg, **kwargs):
        print("[dbupdater#error]", msg.format(**kwargs))

    def critical(self, msg, **kwargs):
        print("[dbupdater#critical]", msg.format(**kwargs))


def dbupdate_v4_to_v5(dbman):
    """Database Updater for v4 to v5.

    This update adds entrance action fields to all exits.

    This is needed for a custom action on entering the destination room.
    """
    # Counters and variables.
    rooms = dbman.rooms.all()
    q = Query()
    exc = 0

    # Perform the updates.
    if len(rooms):
        # Add an entrance action field to every exit.
        for thisroom in rooms:
            for exitid in range(len(thisroom["exits"])):
                thisroom["exits"][exitid]["action"]["entrance"] = ""
                exc += 1
            dbman.upsert_room(thisroom)
        print("Added an entrance action field to {0} exits in {1} rooms.".format(exc, len(rooms)))

        # We are finished, so update the database version record.
        info_record = dbman._info.all()[0]
        info_record["version"] = UPDATE_TO_VERSION
        dbman._info.upsert(info_record, q.version == dbman._UPDATE_FROM_VERSION)

    # The database is actually empty. Do nothing.
    else:
        print("No users.")


def main():
    """Main Program
    """
    print("Dennis 2D Database Updater v4 -> v5")

    # Check command line arguments, and give help if needed.
    if len(sys.argv) != 2 or sys.argv[1] in ["help", "-h", "--help", "-help", "?", "-?"]:
        print("This updater adds entrance action fields to exits.")
        print("Usage: {0} <database>".format(sys.argv[0]))
        return 0

    # Make sure the database file exists.
    if not path.exists(sys.argv[1]):
        print("Database file does not exist: {0}".format(sys.argv[1]))
        return 2

    # Start up DatabaseManager and tell it we're accepting a v4 database for migration to v5.
    dbman = database.DatabaseManager(sys.argv[1], log=Log())
    dbman._UPDATE_FROM_VERSION = 4
    sres = dbman._startup()
    if not sres:
        return 3

    # Run the updates for this migration.
    print("Performing database updates...")
    dbupdate_v4_to_v5(dbman)

    # Finished.
    print("Successfully updated database from v4 to v5: {0}".format(sys.argv[1]))
    dbman._unlock()


if __name__ == "__main__":
    sys.exit(main())
