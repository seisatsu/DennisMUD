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
            e["owners"] = r["owners"]
        r["keys"] = []
        r["sealed"] = False
        dbman.upsert_room(r)
users = dbman.users.find()
if users.count():
    for u in users:
        u["keys"] = []
        dbman.upsert_user(u)
