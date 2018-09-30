import database
import json

with open("cli.config.json") as f:
    config = json.load(f)

dbman = database.DatabaseManager(config["database"]["host"], config["database"]["port"], config["database"]["name"])

# Reset users.
users = dbman.users.find()
if users.count():
    for u in users:
        u["chat"] = {"enabled": True, "ignored": []}
        dbman.upsert_user(u)
