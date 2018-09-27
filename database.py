from pymongo import MongoClient


class DatabaseManager:
    def __init__(self, host, port, dbname):
        self.client = MongoClient(host, port)
        self.database = self.client[dbname]
        self.rooms = self.database["rooms"]
        self.users = self.database["users"]
        self.items = self.database["items"]
        self.inbound = self.database["inbound"]
        self.outbound = self.database["outbound"]

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

    def get_inbound(self, user):
        data = self.inbound.find_one({"user": user})
        if data:
            return dict(data)

    def get_outbound(self, user):
        data = self.outbound.find_one({"user": user})
        if data:
            return dict(data)

    def reset_inbound(self, user):
        self.inbound.update_one({"user": user}, {"$set": {"user": user, "commands": []}}, upsert=True)

    def reset_outbound(self, user):
        self.outbound.update_one({"user": user}, {"$set": {"user": user, "messages": []}}, upsert=True)

    def append_inbound(self, user, command):
        data = self.inbound.find_one({"user": user})
        if data:
            data = dict(data)
        else:
            return None
        if not data["commands"]:
            data["commands"] = [command]
        else:
            data["commands"].append(command)
        self.inbound.update_one({"user": user},
                                {"$set": {"user": user, "commands": data["commands"]}}, upsert=True)

    def append_outbound(self, user, message):
        data = self.outbound.find_one({"user": user})
        if data:
            data = dict(data)
        else:
            return None
        if not data["messages"]:
            data["messages"] = [message]
        else:
            data["messages"].append(message)
        self.outbound.update_one({"user": user},
                                {"$set": {"user": user, "messages": data["messages"]}}, upsert=True)

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

    def _init_room(self):
        newroom = {
            "owner": "<world>",
            "id": 0,
            "name": "Initial Room",
            "desc": "",
            "users": ["<world>"],
            "exits": [],
            "items": [],
        }
        self.rooms.insert_one(newroom)
        return True

    def _init_user(self):
        newuser = {
            "name": "<world>",
            "nick": "Root User",
            "desc": "The administrator.",
            "passhash": "0",
            "online": False,
            "room": 0,
            "inventory": [],
            "wizard": True
        }
        self.users.insert_one(newuser)
        return True
