import blitzdb
import console
import database
import json
import time
from datatype import Exchange


# Read the config file.
with open("web.config.json") as f:
    config = json.load(f)

# Open the Dennis main database.
dbman = database.DatabaseManager(config["database"])


class Router:
    def __init__(self, exchange):
        self.exchange = exchange
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

    def register(self, username, nickname):
        self.users[username] = console.Console(dbman, nickname, self)

    def message(self, nickname, msg):
        self.exchange.outbound[nickname].append(msg)
        self.exchange.save()
        database.commit()

    def broadcast_all(self, msg):
        for u in self.users:
            if not self.users[u].user:
                continue
            self.exchange.outbound[self.users[u].rname].append(msg)

    def broadcast_room(self, room, msg):
        for u in self.users:
            if not self.users[u].user:
                continue
            if self.users[u].user.room == room:
                self.exchange.outbound[self.users[u].rname].append(msg)


# Open the BlitzDB data exchange database.
database = blitzdb.FileBackend(config["exchange"])

# If the exchange document does not exist, make it, otherwise, reset it.
exchange = database.filter(Exchange, {})
if len(exchange) == 0:
    exchange = Exchange({
        "inbound": {},  # username = str: commands = list[str]
        "outbound": {}  # username = str: messages = list[str]
    })
    database.save(exchange)
    database.commit()

else:
    exchange = exchange[0]
    exchange["inbound"] = {}
    exchange["outbound"] = {}
    exchange.save()
    database.commit()

router = Router(exchange)

while True:
    exchange = database.filter(Exchange, {})
    exchange = exchange[0]
    for username in exchange["inbound"]:
        if not username in exchange["outbound"]:
            exchange["outbound"][username] = []
        print(username)
        if username not in router:
            router.register(username, username)
        for cmd in exchange["inbound"][username]:
            router[username].command(cmd)
        exchange["inbound"][username] = []
        exchange.save()
        database.commit()
        time.sleep(0.1)
