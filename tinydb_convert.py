#####################
# Dennis MUD        #
# tinydb_convert.py #
# Copyright 2020    #
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

# This is a very dirty conversion from MongoDB to TinyDB.

import database
import json
from tinydb import TinyDB, Query

tdb = TinyDB("tinydb_out.json")


with open("cli.config.json") as f:
    config = json.load(f)

dbman = database.DatabaseManager(config["database"]["host"], config["database"]["port"],
                                 config["database"]["name"], config["database"]["auth"]["enabled"],
                                 config["database"]["auth"]["user"], config["database"]["auth"]["password"],
                                 config["database"]["auth"]["source"], config["database"]["auth"]["mechanism"])


# Stops eval() from whining.
def ObjectId(whocares):
    pass


# Terrible and unsafe and I feel bad about it but I only have to do it once.
users = dbman.users.find()
tu = tdb.table("users")
if users.count():
    for u in users:
        u2 = eval(u.__repr__())
        del u2["_id"]
        tu.insert(u2)

rooms = dbman.rooms.find()
tr = tdb.table("rooms")
if rooms.count():
    for r in rooms:
        r2 = eval(r.__repr__())
        del r2["_id"]
        tr.insert(r2)

items = dbman.items.find()
ti = tdb.table("items")
if items.count():
    for i in items:
        i2 = eval(i.__repr__())
        del i2["_id"]
        ti.insert(i2)

