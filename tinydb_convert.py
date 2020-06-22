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

import json
import sys
import traceback
from pymongo import MongoClient
from pymongo.errors import ConfigurationError
from tinydb import TinyDB

tdb = TinyDB("tinydb_out.json")


class DatabaseManagerStump:
    """Legacy PyMongo Database Manager Stump
    This manager handles interactions with a MongoDB database corresponding to the current game world.
    Attributes:
        client: The MongoClient which will be used to connect to the database.
        database: The database to use for game data.
        rooms: The collection of all rooms in the database.
        users: The collection of all users in the database.
        items: The collection of all items in the database.
    """
    def __init__(self, host, port, dbname, auth=False, user=None, password=None, source=None, mechanism=None):
        """Database Manager Initializer
        :param host: The hostname of the MongoDB database.
        :param port: The port of the MongoDB database.
        :param dbname: The name of the MongoDB database.
        :param auth: Whether to use MongoDB authentication. (optional, default False.)
        :param user: The username for MongoDB authentication. (required if auth is True)
        :param password: The password for MongoDB authentication. (required if auth is True)
        :param source: The auth source for MongoDB authentication. (required if auth is True)
        :param mechanism: The mechanism for MongoDB authentication. Can be either "SCRAM-SHA-1" or "SCRAM-SHA-256".
            (required if auth is True)
        """
        # Try to connect. This could fail with authentication enabled on old versions of PyMongo that ship with Debian.
        try:
            if auth:
                self.client = MongoClient(host, port, username=user, password=password, authSource=source,
                                          authMechanism=mechanism)
            else:
                self.client = MongoClient(host, port)
        except ConfigurationError:
            print("exiting: mongo configuration failed; your pymongo may be outdated")
            print(traceback.format_exc(1))
            sys.exit(1)

        self.database = self.client[dbname]
        self.rooms = self.database["rooms"]
        self.users = self.database["users"]
        self.items = self.database["items"]


# Load DB configuration from cli.config.json (must point to MongoDB)
with open("cli.config.json") as f:
    config = json.load(f)

# Use the stump to make a connection and load the database.
dbman = DatabaseManagerStump(config["database"]["host"], config["database"]["port"],
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

