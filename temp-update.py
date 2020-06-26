#####################
# Dennis MUD        #
# temp-update.py    #
# Copyright 2018    #
# Michael D. Reiley #
#####################

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

# DO NOT USE!
# This file is modified and used once for updating the database of my test instance every time a change is made to the
# database structure. It is not expected to be safe or useful for whatever particular version you happen to be running
# at the moment. Once Dennis starts having alpha releases with version numbers, there will be safe upgrade scripts.

import database
import json

from tinydb import Query
from tinydb.operations import delete


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


with open("cli.config.json") as f:
    config = json.load(f)

dbman = database.DatabaseManager(config["database"]["filename"], Log())

# Update items.
users = dbman.users.all()
i = 0
q = Query()
if len(users):
    for u in users:
        if "online" in u:
            i += 1
            print(u["name"])
            dbman.users.update(delete("online"), q.name==u["name"])

print("Updated {0} records.".format(i))
dbman._unlock()
