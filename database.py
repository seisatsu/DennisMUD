#####################
# Dennis MUD        #
# database.py       #
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

import json
import sys
from tinydb import TinyDB, Query


class DatabaseManager:
    """The Database Manager

    This manager handles interactions with a TinyDB database corresponding to the current game world.

    Attributes:
        database: The database to use for game data.
        rooms: The table of all rooms in the database.
        users: The table of all users in the database.
        items: The table of all items in the database.
    """
    def __init__(self, filename):
        """Database Manager Initializer

        :param filename: The relative or absolute filename of the TinyDB database file.
        """
        # See if we can access the database file.
        try:
            with open(filename, "a") as f:
                pass
        except:
            print("exiting: could not open database file: ", filename)
            sys.exit(1)

        self.database = TinyDB(filename)
        self.rooms = self.database.table("rooms")
        self.users = self.database.table("users")
        self.items = self.database.table("items")

        # Try to load the defaults config file.
        try:
            with open("defaults.config.json") as f:
                self.defaults = json.load(f)
        except:
            print("exiting: could not open defaults file")
            sys.exit(1)

        # If there are no rooms, make the initial room.
        if len(self.rooms.all()) == 0:
            self._init_room()

        # If there are no users, make the root user.
        if len(self.users.all()) == 0:
            self._init_user()

    def upsert_room(self, document):
        """Update or insert a room.

        :param document: The room document to update or insert.
        :return: True
        """
        q = Query()
        self.rooms.upsert(document, q.id == document["id"])
        return True

    def upsert_item(self, document):
        """Update or insert an item.

        :param document: The item document to update or insert.
        :return: True
        """
        q = Query()
        self.items.upsert(document, q.id == document["id"])
        return True

    def upsert_user(self, document):
        """Update or insert a user.

        :param document: The user document to update or insert.
        :return: True
        """
        q = Query()
        self.users.upsert(document, q.name == document["name"])
        return True

    def delete_room(self, document):
        """Delete a room.

        :param document: The room document to delete.
        :return: True
        """
        q = Query()
        self.rooms.remove(q.id == document["id"])
        return True

    def delete_item(self, document):
        """Delete an item.

        :param document: The item document to delete.
        :return: True
        """
        q = Query()
        self.items.remove(q.id == document["id"])
        return True

    def delete_user(self, document):
        """Delete a user.

        :param document: The user document to delete.
        :return: True
        """
        q = Query()
        self.users.remove(q.name == document["name"])
        return True

    def room_by_id(self, roomid):
        """Get a room by its id.

        :param roomid: The id of the room to retrieve from the database.
        :return: Room document or None.
        """
        q = Query()
        return self.rooms.search(q.id == roomid)[0]

    def item_by_id(self, itemid):
        """Get an item by its id.

        :param itemid: The id of the item to retrieve from the database.
        :return: Item document or None.
        """
        q = Query()
        return self.items.search(q.id == itemid)[0]

    def user_by_name(self, username):
        """Get a user by their name.

        If there is any chance the user could be logged in, and the record needs to be altered,
        you should use the equivalent Console method. This method is faster but unsafe for logged in users.

        :param username: The name of the user to retrieve from the database.
        :return: User document or None.
        """
        users = self.users.all()
        if len(users):
            for u in users:
                if u["name"].lower() == username.lower():
                    return u
        return None

    def user_by_nick(self, nickname):
        """Get a user by their nickname.

        If there is any chance the user could be logged in, and the record needs to be altered,
        you should use the equivalent Console method. This method is faster but unsafe for logged in users.

        :param nickname: The nickname of the user to retrieve from the database.
        :return: User document or None.
        """
        users = self.users.all()
        if len(users):
            for u in users:
                if u["nick"].lower() == nickname.lower():
                    return u
        return None

    def auth_user(self, username, passhash):
        """Check if a username and password match an existing user.

        :param username: The name of the user to authenticate.
        :param passhash: The hashed password of the user to authenticate.
        :return: User document or None.
        """
        u = self.user_by_name(username)
        if not u:
            return None
        if u["passhash"] != passhash:
            return None
        return u

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
        self.rooms.insert(newroom)
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
            "autolook": {
                "enabled": self.defaults["first_user"]["autolook"]["enabled"]
            },
            "chat": {
                "enabled": self.defaults["first_user"]["chat"]["enabled"],
                "ignored": []
            },
            "wizard": True
        }
        self.users.insert(newuser)
        return True
