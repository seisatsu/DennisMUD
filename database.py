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

from pymongo import MongoClient


class DatabaseManager:
    def __init__(self, host, port, dbname):
        self.client = MongoClient(host, port)
        self.database = self.client[dbname]
        self.rooms = self.database["rooms"]
        self.users = self.database["users"]
        self.items = self.database["items"]

        if self.database.rooms.find().count() == 0:
            self._init_room()

        if self.database.users.find().count() == 0:
            self._init_user()

    def upsert_room(self, document):
        # Update or insert a room.
        self.rooms.update_one({"id": document["id"]}, {"$set": document}, upsert=True)

    def upsert_item(self, document):
        # Update or insert an item.
        self.items.update_one({"id": document["id"]}, {"$set": document}, upsert=True)

    def upsert_user(self, document):
        # Update or insert a user.
        self.users.update_one({"name": document["name"]}, {"$set": document}, upsert=True)

    def delete_room(self, document):
        # Delete a room.
        self.rooms.delete_one({"id": document["id"]})

    def delete_item(self, document):
        # Delete an item.
        self.items.delete_one({"id": document["id"]})

    def delete_user(self, document):
        # Delete a user.
        self.users.delete_one({"name": document["name"]})

    def room_by_id(self, roomid):
        # Get a room by its ID
        return self.rooms.find_one({"id": roomid})

    def item_by_id(self, itemid):
        # Get an item by its ID
        return self.items.find_one({"id": itemid})

    def user_by_name(self, username):
        # Get a user by their name.
        users = self.users.find()
        if users.count():
            for u in users:
                if u["name"].lower() == username.lower():
                    return u
        return None

    def user_by_nick(self, nickname):
        # Get a user by their nickname.
        users = self.users.find()
        if users.count():
            for u in users:
                if u["nick"].lower() == nickname.lower():
                    return u
        return None

    def _init_room(self):
        newroom = {
            "owners": ["<world>"],
            "id": 0,
            "name": "Initial Room",
            "desc": "",
            "users": ["<world>"],
            "exits": [],
            "items": [],
            "keys": [],
            "locked": False,
            "sealed": False
        }
        self.rooms.insert_one(newroom)
        return True

    def _init_user(self):
        newuser = {
            "name": "<world>",
            "nick": "Root User",
            "desc": "The first user and administrator.",
            "passhash": "0",
            "online": False,
            "room": 0,
            "inventory": [],
            "keys": [],
            "chat": {
                "enabled": True,
                "ignored": []
            },
            "wizard": True
        }
        self.users.insert_one(newuser)
        return True
