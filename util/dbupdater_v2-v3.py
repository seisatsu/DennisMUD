######################
# Dennis MUD         #
# dbupdater_v2-v3.py #
# Copyright 2020     #
# Sei Satzparad      #
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

# This is the Dennis 2D Database Updater for v2 -> v3 migration.
# To use it, copy it into your main Dennis directory and run it
# with the database filename as its only argument. This updater
# adds a telekey field to all items.

from os import path
import sys

from tinydb import Query

try:
    from lib import database
except:
    print("Can't find DatabaseManager. You should move this script to the Dennis root directory.")
    sys.exit(1)


UPDATE_TO_VERSION = 3


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


def dbupdate_v2_to_v3(dbman):
    """Database Updater for v2 to v3.

    This update adds an empty "telekey" field to all items.

    This is needed for telekeys.
    """
    # Counters and variables.
    items = dbman.items.all()
    q = Query()

    # Perform the updates.
    if len(items):
        # Add an empty telekey field to every item.
        for thisitem in items:
            thisitem["telekey"] = None
            dbman.upsert_item(thisitem)
        print("Added an empty telekey field to {0} items.".format(len(items)))

        # We are finished, so update the database version record.
        info_record = dbman._info.all()[0]
        info_record["version"] = UPDATE_TO_VERSION
        dbman._info.upsert(info_record, q.version == dbman._UPDATE_FROM_VERSION)

    # The database is actually empty. Do nothing.
    else:
        print("No items.")


def main():
    """Main Program
    """
    print("Dennis 2D Database Updater v2 -> v3")

    # Check command line arguments, and give help if needed.
    if len(sys.argv) != 2 or sys.argv[1] in ["help", "-h", "--help", "-help", "?", "-?"]:
        print("This updater adds telekey fields to items for the telekey feature.")
        print("Usage: {0} <database>".format(sys.argv[0]))
        return 0

    # Make sure the database file exists.
    if not path.exists(sys.argv[1]):
        print("Database file does not exist: {0}".format(sys.argv[1]))
        return 2

    # Start up DatabaseManager and tell it we're accepting a v2 database for migration.
    dbman = database.DatabaseManager(sys.argv[1], Log())
    dbman._UPDATE_FROM_VERSION = 2
    sres = dbman._startup()
    if not sres:
        return 3

    # Run the updates for this migration.
    dbupdate_v2_to_v3(dbman)

    # Finished.
    print("Successfully updated database from v2 to v3: {0}".format(sys.argv[1]))
    dbman._unlock()


if __name__ == "__main__":
    sys.exit(main())
