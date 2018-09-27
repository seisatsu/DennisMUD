import console
import database
import json
import time


# Read the config file.
with open("web.config.json") as f:
    config = json.load(f)

# Open the Dennis main database.
dbman = database.DatabaseManager(config["database"]["host"], config["database"]["port"], config["database"]["name"])


class Router:
    def __init__(self):
        self.users = {}

    def __contains__(self, item):
        if item in self.users:
            return True
        return False

    def __getitem__(self, item):
        if self.__contains__(item):
            return self.users[item]
        else:
            return None

    def __iter__(self):
        return self.users.items()

    def register(self, username):
        self.users[username] = console.Console(dbman, username, self)

    def message(self, username, msg):
        dbman.append_outbound(username, msg)
        print(dbman.get_outbound(username))

    def broadcast_all(self, msg):
        for u in self.users:
            if not self.users[u].user:
                continue
            dbman.append_outbound(self.users[u].rname, msg)

    def broadcast_room(self, room, msg):
        for u in self.users:
            if not self.users[u].user:
                continue
            if self.users[u].user.room == room:
                dbman.append_outbound(self.users[u].rname, msg)


# Completely reset the inbound and outbound exchanges.
dbman.inbound.remove({})
dbman.outbound.remove({})

router = Router()

while True:
    for user in list(dbman.inbound.find()):
        if not dbman.get_outbound(user["user"]):
            dbman.reset_outbound(user["user"])
        if user["user"] not in router:
            router.register(user["user"])
        if user["commands"]:
            for cmd in user["commands"]:
                router[user["user"]].command(cmd)
            dbman.reset_inbound(user["user"])
        time.sleep(0.1)
