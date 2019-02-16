#####################
# Dennis MUD        #
# database.py       #
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

import json
import sys
from pymongo import MongoClient
from pymongo.errors import ConfigurationError, OperationFailure


class DatabaseManager:
    """The Database Manager

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
            sys.exit(1)

        self.database = self.client[dbname]
        self.rooms = self.database["rooms"]
        self.users = self.database["users"]
        self.items = self.database["items"]

        # Try to load the defaults config file.
        try:
            with open("defaults.config.json") as f:
                self.defaults = json.load(f)
        except:
            print("exiting: could not open defaults file")
            sys.exit(1)

        # If there are no rooms, make the initial room. Also tests authentication.
        try:
            if self.database.rooms.find().count() == 0:
                self._init_room()
        except OperationFailure:
            print("exiting: failed to access database; authentication may be required")
            sys.exit(1)

        # If there are no users, make the root user.
        if self.database.users.find().count() == 0:
            self._init_user()

    def upsert_room(self, document):
        """Update or insert a room.

        :param document: The room document to update or insert.
        :return: True
        """
        self.rooms.update_one({"id": document["id"]}, {"$set": document}, upsert=True)
        return True

    def upsert_item(self, document):
        """Update or insert an item.

        :param document: The item document to update or insert.
        :return: True
        """
        self.items.update_one({"id": document["id"]}, {"$set": document}, upsert=True)
        return True

    def upsert_user(self, document):
        """Update or insert a user.

        :param document: The user document to update or insert.
        :return: True
        """
        self.users.update_one({"name": document["name"]}, {"$set": document}, upsert=True)
        return True

    def delete_room(self, document):
        """Delete a room.

        :param document: The room document to delete.
        :return: True
        """
        self.rooms.delete_one({"id": document["id"]})
        return True

    def delete_item(self, document):
        """Delete an item.

        :param document: The item document to delete.
        :return: True
        """
        self.items.delete_one({"id": document["id"]})
        return True

    def delete_user(self, document):
        """Delete a user.

        :param document: The user document to delete.
        :return: True
        """
        self.users.delete_one({"name": document["name"]})
        return True

    def room_by_id(self, roomid):
        """
        Get a room by its id.

        :param roomid: The id of the room to retrieve from the database.
        :return: Room document or None.
        """
        return self.rooms.find_one({"id": roomid})

    def item_by_id(self, itemid):
        """
        Get an item by its id.

        :param itemid: The id of the item to retrieve from the database.
        :return: Room document or None.
        """
        return self.items.find_one({"id": itemid})

    def user_by_name(self, username):
        """
        Get a user by their name.

        :param username: The name of the user to retrieve from the database.
        :return: User document or None.
        """
        users = self.users.find()
        if users.count():
            for u in users:
                if u["name"].lower() == username.lower():
                    return u
        return None

    def user_by_nick(self, nickname):
        """
        Get a user by their nickname.

        :param nickname: The nickname of the user to retrieve from the database.
        :return: User document or None.
        """
        users = self.users.find()
        if users.count():
            for u in users:
                if u["nick"].lower() == nickname.lower():
                    return u
        return None

    def _init_room(self):
        """Initialize the world with the first room.

        :return: True
        """
        newroom = {
            "owners": ["<world>"],
            "id": 0,
            "name": self.defaults["first_room"]["name"],
            "desc": self.defaults["first_room"]["desc"],
            "users": [self.defaults["first_user"]["name"]],
            "exits": [],
            "items": [],
            "sealed": {
                "inbound": self.defaults["first_room"]["sealed"]["inbound"],
                "outbound": self.defaults["first_room"]["sealed"]["outbound"]
            }
        }
        self.rooms.insert_one(newroom)
        return True

    def _init_user(self):
        """Initialize the world with the root user.

        :return: True
        """
        newuser = {
            "name": self.defaults["first_user"]["name"],
            "nick": self.defaults["first_user"]["nick"],
            "desc": self.defaults["first_user"]["desc"],
            "passhash": "0",
            "online": False,
            "room": 0,
            "inventory": [],
            "chat": {
                "enabled": self.defaults["first_user"]["chat"]["enabled"],
                "ignored": []
            },
            "wizard": True
        }
        self.users.insert_one(newuser)
        return True
