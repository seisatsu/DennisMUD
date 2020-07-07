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
import traceback

from tinydb import TinyDB, Query

from twisted.logger import Logger

DB_VERSION = 4


class DatabaseManager:
    """The Database Manager

    This manager handles interactions with a TinyDB database corresponding to the current game world.
    After documents are pulled from a table and modified, they need to be upserted for the changes to save.

    :ivar database: The TinyDB database instance for the world.
    :ivar rooms: The table of all rooms in the database.
    :ivar users: The table of all users in the database.
    :ivar items: The table of all items in the database.
    :ivar defaults: The JSON database defaults configuration.
    """
    def __init__(self, filename, log=None):
        """Database Manager Initializer

        :param filename: The relative or absolute filename of the TinyDB database file.
        :param log: Alternative logging facility, if set. Otherwise use the Twisted logger.
        """
        self.database = None
        self.rooms = None
        self.users = None
        self.items = None
        self.defaults = None

        self._info = None
        self._users_online = []
        self._filename = filename
        self._log = log or Logger("database")
        self._rooms_cleaned = []
        self._locked = False

        # This will be changed when running an update tool.
        self._UPDATE_FROM_VERSION = DB_VERSION

    def _startup(self):
        """Perform startup tasks.

        Startup tasks for the DatabaseManager that can fail are put here,
        so that we can catch a return code and exit cleanly on failure.

        :return: True if succeeded, False if failed, None if failed due to existing lockfile.
        """
        # Try to load the defaults config file. If we can't, then fail.
        try:
            with open("defaults.config.json") as f:
                self.defaults = json.load(f)
        except (OSError, IOError):
            self._log.critical("Could not open defaults config file: defaults.config.json")
            self._log.critical(traceback.format_exc(1))
            return False
        except json.JSONDecodeError:
            self._log.critical("JSON error from config file: defaults.config.json")
            self._log.critical(traceback.format_exc(1))
            return False

        # Check if a lockfile exists for this database. If so, then fail.
        if os.path.exists(self._filename + ".lock"):
            self._log.critical("Lockfile exists for database: {filename}", filename=self._filename)
            self._log.critical(
                "If you are sure the database isn't in use, delete this file: {filename}.lock", filename=self._filename)
            return None

        # See if we can access the database file. If not, then fail.
        try:
            with open(self._filename, "a") as f:
                pass
        except:
            self._log.critical("Could not open database file: {filename}", filename=self._filename)
            self._log.critical(traceback.format_exc(1))
            return False

        # Attempt to create the lockfile. If we can't, then fail.
        try:
            with open(self._filename + ".lock", "a") as f:
                self._locked = True
        except:
            self._log.critical("Could not create lockfile for database: {filename}", filename=self._filename)
            self._log.critical(traceback.format_exc(1))
            return False

        self._log.info("Loading database: {filename}", filename=self._filename)

        # Try to load the database file. If an error occurs, fail.
        try:
            self.database = TinyDB(self._filename)
        except:
            self._log.critical("Error from TinyDB while loading database: {filename}", filename=self._filename)
            self._log.critical(traceback.format_exc(1))
            return False

        # Load the rooms, users, items, and _info tables.
        self.rooms = self.database.table("rooms")
        self.users = self.database.table("users")
        self.items = self.database.table("items")
        self._info = self.database.table("_info")

        # If the info table is empty, assume a new database and add an info record containing the current version.
        if len(self._info.all()) == 0:
            self._info.insert({"version": DB_VERSION})

        # Otherwise read out the existing info record and check if it's ok.
        else:
            info_record = self._info.all()[0]

            # This either needs to be the current version or the version we are updating from.
            # The _UPDATE_FROM_VERSION variable is identical to the current database version,
            # except when we are running an updater script. If _UPDATE_FROM_VERSION is identical
            # to the current database version, we are running normally and loading a database of
            # the correct version, so we can skip this whole section.
            if info_record["version"] != self._UPDATE_FROM_VERSION:
                # An updater is trying to update the database, but the database is already up to date. Fail.
                if info_record["version"] == DB_VERSION:
                    self._log.critical("Database is already up to date, doing nothing.")

                # An updater is trying to update a database of the wrong version. Fail.
                elif self._UPDATE_FROM_VERSION != DB_VERSION:
                    self._log.critical("Trying to update from v{oldver} to v{newver}, but detected v{filever}.",
                                       oldver=self._UPDATE_FROM_VERSION, newver=DB_VERSION,
                                       filever=info_record["version"])

                # No updater is running, we are just trying to load a database of the wrong version. Fail.
                else:
                    self._log.critical("Database version mismatch, v{filever} detected, v{currver} required.",
                                       filever=info_record["version"], currver=self._UPDATE_FROM_VERSION)
                    self._log.critical("Check the util folder for a dbupdate script to migrate between these versions.")

                # Remove the lockfile before exiting.
                self._unlock()
                return False

        # If there are no rooms, make the initial room.
        if len(self.rooms.all()) == 0:
            self._log.info("Initializing rooms table.")
            self._init_room()

        # If there are no users, make the root user.
        if len(self.users.all()) == 0:
            self._log.info("Initializing users table.")
            self._init_user()

        # Finished starting up.
        self._log.info("Finished loading database.")
        return True

    def upsert_room(self, document):
        """Update or insert a room.

        If the room exists, it will be updated, otherwise it will be inserted.
        The key is the room ID.

        :param document: The room document to update or insert.

        :return: True
        """
        q = Query()
        self.rooms.upsert(document, q.id == document["id"])
        return True

    def upsert_item(self, document):
        """Update or insert an item.

        If the item exists, it will be updated, otherwise it will be inserted.
        The key is the item ID.

        :param document: The item document to update or insert.

        :return: True
        """
        q = Query()
        self.items.upsert(document, q.id == document["id"])
        return True

    def upsert_user(self, document):
        """Update or insert a user.

        If the user exists, it will be updated, otherwise it will be inserted.
        The key is the username.

        :param document: The user document to update or insert.

        :return: True
        """
        q = Query()
        self.users.upsert(document, q.name == document["name"])
        return True

    def delete_room(self, document):
        """Delete a room.

        :param document: The room document to delete.

        :return: True if succeeded, False if the document didn't exist.
        """
        q = Query()
        removed = self.rooms.remove(q.id == document["id"])
        if not removed:
            return False
        return True

    def delete_item(self, document):
        """Delete an item.

        :param document: The item document to delete.

        :return: True if succeeded, False if the document didn't exist.
        """
        q = Query()
        removed = self.items.remove(q.id == document["id"])
        if not removed:
            return False
        return True

    def delete_user(self, document):
        """Delete a user.

        This is not safe to call while the user is online.

        :param document: The user document to delete.

        :return: True if succeeded, False if the document didn't exist.
        """
        q = Query()
        removed = self.users.remove(q.name == document["name"])
        if not removed:
            return False
        return True

    def room_by_id(self, roomid, clean=True):
        """Get a room by its id.

        :param roomid: The id of the room to retrieve from the database.
        :param clean: Whether to automatically remove offline user records. Should usually be True.

        :return: Room document or None.
        """
        # Search for a room in the database whose ID is the given ID. Assume only one exists.
        q = Query()
        thisroom = self.rooms.search(q.id == roomid)

        # Couldn't find a room with that ID, so return nothing.
        if not thisroom:
            return None

        # TinyDB always returns a list, so take the first item.
        thisroom = thisroom[0]

        # If we are not automatically removing offline users from this room, then return the room document right away.
        # Cleaning offline users is usually only disabled for debugging purposes, for example to grab a corrupted
        # room document that won't make it through cleaning so that we can pass it to delete_room().
        if not clean:
            return thisroom

        # For each user in the room, check if they are online. If not, remove them. This used to be done for every room
        # at startup, and took a long time. It is much faster to do it as needed, though not doing it at startup leaves
        # quasi-online ghost users in the record of each room until it is loaded. This doesn't actually matter though.
        # After we do this once, we take note so we don't have to do it again during this server session.
        if roomid not in self._rooms_cleaned:
            for username in thisroom["users"]:
                user = self.user_by_name(username)
                if user and username not in self._users_online:
                    thisroom["users"].remove(username)

            # Save the room after cleaning out the offline users, and then grab it again.
            self.upsert_room(thisroom)
            self._rooms_cleaned.append(roomid)
            thisroom = self.rooms.search(q.id == roomid)[0]

        # Return the cleaned room document.
        return thisroom

    def item_by_id(self, itemid):
        """Get an item by its id.

        :param itemid: The id of the item to retrieve from the database.

        :return: Item document or None.
        """
        q = Query()
        thisitem = self.items.search(q.id == itemid)
        if not thisitem:
            return None
        return thisitem[0]

    def user_by_name(self, username):
        """Get a user by their name.

        If there is any chance the user could be logged in, and their record needs to be altered,
        you should use the equivalent Console method instead. This method is faster but won't update logged in users.

        :param username: The name of the user to retrieve from the database.

        :return: User document or None.
        """
        allusers = self.users.all()
        for user in allusers:
            if user["name"].lower() == username.lower():
                return user
        return None

    def user_by_nick(self, nickname):
        """Get a user by their nickname.

        If there is any chance the user could be logged in, and their record needs to be altered,
        you should use the equivalent Console method instead. This method is faster but won't update logged in users.

        :param nickname: The nickname of the user to retrieve from the database.

        :return: User document or None.
        """
        allusers = self.users.all()
        for user in allusers:
            if user["nick"].lower() == nickname.lower():
                return user
        return None

    def login_user(self, username, passhash):
        """Check if a username and password match an existing user, and log them in.

        The Database Manager keeps track of which users are online.

        :param username: The name of the user to log in.
        :param passhash: The hashed password of the user to log in.

        :return: User document if succeeded, None if failed.
        """
        username = username.lower()
        thisuser = self.user_by_name(username)

        # This user does not exist.
        if not thisuser:
            return None

        # Bad credentials.
        if thisuser["passhash"] != passhash:
            return None

        # Attempt to log in a user who is already logged in.
        if username in self._users_online:
            self._log.warn("User logged in twice: {username}", username=username)
            return None

        # Clean and successful login.
        else:
            self._users_online.append(username)
            return thisuser

    def logout_user(self, username):
        """Log out a user.

        :param username: The name of the user to log out.

        :return: True if succeeded, False if failed.
        """
        username = username.lower()
        thisuser = self.user_by_name(username)

        # User does not exist.
        if not thisuser and username not in self._users_online:
            return False

        # User does not exist, but they are online anyway for some reason.
        # Still return True since we logged them out.
        elif not thisuser and username in self._users_online:
            self._log.warn("Nonexistent user was online: {username}", username=username)
            self._users_online.remove(username)
            return True

        # Attempt to log out user who was not logged in.
        elif username not in self._users_online:
            self._log.warn("User logged out twice: {username}", username=username)
            return False

        # Clean and successful logout.
        else:
            self._users_online.remove(username)
            return True

    def online(self, username):
        """Check if a user is online.

        :param username: The name of the user to check.

        :return: True if online, False if offline.
        """
        if username.lower() in self._users_online:
            return True
        return False

    def _init_room(self):
        """Initialize the world with the first room, taking defaults from the defaults config file.

        :return: True
        """
        newroom = {
            "owners": ["<world>"],
            "id": 0,
            "name": self.defaults["first_room"]["name"],
            "desc": self.defaults["first_room"]["desc"],
            "users": [self.defaults["first_user"]["name"]],
            "exits": [],
            "entrances": [],
            "items": [],
            "sealed": {
                "inbound": self.defaults["first_room"]["sealed"]["inbound"],
                "outbound": self.defaults["first_room"]["sealed"]["outbound"]
            }
        }
        self.rooms.insert(newroom)
        return True

    def _init_user(self):
        """Initialize the world with the root user, taking defaults from the defaults config file.

        :return: True
        """
        newuser = {
            "name": "<world>",
            "nick": self.defaults["first_user"]["nick"],
            "desc": self.defaults["first_user"]["desc"],
            "passhash": "0",
            "room": 0,
            "inventory": [],
            "autolook": {
                "enabled": self.defaults["first_user"]["autolook"]["enabled"]
            },
            "chat": {
                "enabled": self.defaults["first_user"]["chat"]["enabled"],
                "ignored": []
            },
            "pronouns": "neutral",
            "wizard": True
        }
        self.users.insert(newuser)
        return True

    def _unlock(self):
        """Clean up the lockfile before exiting.

        :return: None
        """
        # We never got around to making a lockfile.
        if not self._locked:
            return

        # The lockfile should not disappear before shutdown.
        if not os.path.exists(self._filename + ".lock"):
            self._log.warn("Lockfile disappeared while running for database: {filename}",
                           filename=self._filename)

        # The lockfile still exists, so attempt to remove it.
        else:
            try:
                os.remove(self._filename + ".lock")

            # Couldn't remove the lockfile. Probably a permissions issue.
            except:
                self._log.warn("Could not delete lockfile for database: {filename}", filename=self._filename)
