#######################
# Dennis MUD          #
# dbupdater_v3-v4.py  #
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

# This is the Dennis 2D Database Updater for v3 -> v4 migration.
# To use it, copy it into your main Dennis directory and run it
# with the database filename as its only argument. This updater
# adds a neutral pronouns field to all users.

from os import path
import sys

from tinydb import Query

try:
    from lib import database
except:
    print("Can't find DatabaseManager. You should move this script to the Dennis root directory.")
    sys.exit(1)


UPDATE_TO_VERSION = 4


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


def dbupdate_v3_to_v4(dbman):
    """Database Updater for v3 to v4.

    This update adds an neutral "pronouns" field to all users.

    This is needed for pronouns used in formatting posturing text.
    """
    # Counters and variables.
    users = dbman.users.all()
    q = Query()

    # Perform the updates.
    if len(users):
        # Add a neutral pronouns field to every user.
        for thisuser in users:
            thisuser["pronouns"] = "neutral"
            dbman.upsert_user(thisuser)
        print("Added a neutral pronouns field to {0} users.".format(len(users)))

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
    print("Dennis 2D Database Updater v3 -> v4")

    # Check command line arguments, and give help if needed.
    if len(sys.argv) != 2 or sys.argv[1] in ["help", "-h", "--help", "-help", "?", "-?"]:
        print("This updater adds neutral pronouns fields to users for formatting posturing text.")
        print("Usage: {0} <database>".format(sys.argv[0]))
        return 0

    # Make sure the database file exists.
    if not path.exists(sys.argv[1]):
        print("Database file does not exist: {0}".format(sys.argv[1]))
        return 2

    # Start up DatabaseManager and tell it we're accepting a v3 database for migration to v4.
    dbman = database.DatabaseManager(sys.argv[1], log=Log())
    dbman._UPDATE_FROM_VERSION = 3
    sres = dbman._startup()
    if not sres:
        return 3

    # Run the updates for this migration.
    print("Performing database updates...")
    dbupdate_v3_to_v4(dbman)

    # Finished.
    print("Successfully updated database from v3 to v4: {0}".format(sys.argv[1]))
    dbman._unlock()


if __name__ == "__main__":
    sys.exit(main())
