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
import os
import sys

from tinydb import TinyDB, Query

from twisted.logger import Logger

DB_VERSION = 1


class DatabaseManager:
    """The Database Manager

    This manager handles interactions with a TinyDB database corresponding to the current game world.
    After documents are pulled from a table and modified, they need to be upserted for the changes to save.

    Attributes:
        database: The database to use for game data.
        rooms: The table of all rooms in the database.
        users: The table of all users in the database.
        items: The table of all items in the database.
        _info: The table of database meta info.
    """
    def __init__(self, filename, log=None):
        """Database Manager Initializer

        :param filename: The relative or absolute filename of the TinyDB database file.
        :param log: Alternative logging facility, if set.
        """
        self._filename = filename
        self._log = log or Logger("database")
        self._rooms_cleaned = []
        self._log.info("initializing database manager")

        # Try to load the defaults config file.
        try:
            with open("defaults.config.json") as f:
                self.defaults = json.load(f)
        except:
            self._log.critical("exiting: could not open defaults file")
            sys.exit(1)

        # Check if a lockfile exists for this database. If so, exit.
        if os.path.exists(filename + ".lock"):
            self._log.critical("exiting: lockfile exists for database: {filename}", filename=filename)
            sys.exit(1)

        # See if we can access the database file.
        try:
            with open(filename, "a") as f:
                pass
        except:
            self._log.critical("exiting: could not open database file: {filename}", filename=filename)
            sys.exit(1)

        # Create the lockfile.
        try:
            with open(filename + ".lock", "a") as f:
                pass
        except:
            self._log.critical("exiting: could not create lockfile for database: {filename}", filename=filename)
            sys.exit(1)

        self._log.info("loading database: {filename}", filename=filename)
        self.database = TinyDB(filename)
        self.rooms = self.database.table("rooms")
        self.users = self.database.table("users")
        self.items = self.database.table("items")
        self._info = self.database.table("_info")

        # If the info table is empty, add a version record. Otherwise, compare versions.
        if len(self._info.all()) == 0:
            self._info.insert({"version": DB_VERSION})
        else:
            q = Query()
            if not self._info.search(q.version == DB_VERSION):
                self._log.critical("exiting: database version mismatch, {theirs} detected, {ours} required",
                          theirs=q.version, ours=DB_VERSION)
                self._unlock()
                sys.exit(1)

        # If there are no rooms, make the initial room.
        if len(self.rooms.all()) == 0:
            self._log.info("initializing rooms table")
            self._init_room()

        # If there are no users, make the root user.
        if len(self.users.all()) == 0:
            self._log.info("initializing users table")
            self._init_user()

        self._log.info("finished loading database")

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
        thisroom = self.rooms.search(q.id == roomid)[0]

        # For each user in the room, check if they are online. If not, remove them. This used to be done for every room
        # at startup, and took a long time. It is much faster to do it as needed, though not doing it at startup leaves
        # quasi-online ghost users in the record of each room until it is loaded. This doesn't actually matter though.
        # After we do this once, we take note so we don't have to do it again during this server session.
        if roomid not in self._rooms_cleaned:
            for username in thisroom["users"]:
                user = self.user_by_name(username)
                if user and not user["online"]:
                    thisroom["users"].remove(username)
            self.upsert_room(thisroom)
            self._rooms_cleaned.append(roomid)
            thisroom = self.rooms.search(q.id == roomid)[0]

        return thisroom

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

    def _unlock(self):
        """Clean up the lockfile before exiting.

        :return: None
        """
        if not os.path.exists(self._filename + ".lock"):
            self._log.warn("lockfile disappeared while running for database: {filename}",
                          filename=self._filename)
            sys.stdout.flush()
        else:
            try:
                os.remove(self._filename + ".lock")
            except:
                self._log.warn("could not delete lockfile for database: {filename}", filename=self._filename)
                sys.stdout.flush()
