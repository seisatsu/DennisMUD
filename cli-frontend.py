import console
import database
import json


class Router:
    def __init__(self):
        pass

    def message(self, nickname, msg):
        pass

    def broadcast_all(self, msg):
        pass

    def broadcast_room(self, room, msg):
        pass


with open("cli.config.json") as f:
    config = json.load(f)

dbman = database.DatabaseManager(config["database"]["host"], config["database"]["port"], config["database"]["name"])

# Reset users.
rooms = dbman.rooms.find()
if rooms.count():
    for r in rooms:
        r["users"] = []
        dbman.upsert_room(r)
users = dbman.users.find()
if users.count():
    for u in users:
        u["online"] = False
        dbman.upsert_user(u)

# Log in as the root user.
dennis = console.Console(dbman, "<world>", Router())
dennis.user = dbman.user_by_name("<world>")
dennis.user["online"] = True
if not dennis.user["wizard"]:
    dennis.user["wizard"] = True
dbman.upsert_user(dennis.user)

while True:
    cmd = input("> ")
    print(dennis.command(cmd))
