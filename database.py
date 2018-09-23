import blitzdb
from datatype import Room, User, Item


class DatabaseManager:
    def __init__(self, database):
        self.database = blitzdb.FileBackend(database)

        if len(self.database.filter(Room, {})) == 0:
            self._init_room()

        if len(self.database.filter(User, {})) == 0:
            self._init_user()

    def insert(self, document):
        # Insert a new document.
        self.database.save(document)
        self.database.commit()

    def update(self, document):
        # Update an existing document.
        document.save()
        self.database.commit()

    def delete(self, document):
        # Delete an existing document.
        self.database.delete(document)
        self.database.commit()

    def filter(self, doctype, query):
        # Perform a query on the database.
        return self.database.filter(doctype, query)

    def room_by_id(self, roomid):
        # Get a room by its ID
        result = self.database.filter(Room, {"id": roomid})
        if len(result):
            return result[0]
        return None

    def item_by_id(self, itemid):
        # Get an item by its ID
        result = self.database.filter(Item, {"id": itemid})
        if len(result):
            return result[0]
        return None

    def user_by_name(self, username):
        # Get a user by their name. (Case insensitive.)
        users = self.database.filter(User, {})
        if len(users):
            for u in users:
                if u["name"].lower() == username.lower():
                    return u
        return None

    def _init_room(self):
        newroom = Room({
            "owner": "[world]",
            "id": 0,
            "name": "Initial Room",
            "desc": "",
            "users": ["[world]"],
            "exits": [],
            "items": [],
        })
        self.insert(newroom)
        return True

    def _init_user(self):
        newuser = User({
            "name": "[world]",
            "nick": "Root User",
            "desc": "The administrator.",
            "passhash": "0",
            "online": False,
            "room": 0,
            "inventory": [],
            "wizard": True
        })
        self.insert(newuser)
        return True
