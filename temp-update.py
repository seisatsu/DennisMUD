import database
import json

with open("cli.config.json") as f:
    config = json.load(f)

dbman = database.DatabaseManager(config["database"]["host"], config["database"]["port"], config["database"]["name"])

# Reset users.
rooms = dbman.rooms.find()
if rooms.count():
    for r in rooms:
        for e in r["exits"]:
            for o in range(len(e["owners"])):
                e["owners"][o] = e["owners"][o].lower()
        for o in range(len(r["owners"])):
            r["owners"][o] = r["owners"][o].lower()
        dbman.upsert_room(r)
users = dbman.users.find()
if users.count():
    for u in users:
        u["name"] = u["name"].lower()
        dbman.upsert_user(u)
items = dbman.items.find()
if items.count():
    for i in items:
        for o in range(len(i["owners"])):
            i["owners"][o] = i["owners"][o].lower()
        dbman.upsert_item(i)
