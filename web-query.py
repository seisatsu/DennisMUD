import cgi
import database
import json
import os
import time

# Use IP address for routing!

# Read the config file.
with open("web.config.json") as f:
    config = json.load(f)

# Retrieve HTTP request fields.
fields = cgi.FieldStorage()

# Open the Dennis main database.
dbman = database.DatabaseManager(config["database"]["host"], config["database"]["port"], config["database"]["name"])

if "DENNIS_TESTCLIENT" in os.environ:
    if not dbman.get_inbound(os.environ["DENNIS_USER"]):
        dbman.reset_inbound(os.environ["DENNIS_USER"])
    if not dbman.get_outbound(os.environ["DENNIS_USER"]):
        dbman.reset_outbound(os.environ["DENNIS_USER"])
    dbman.append_inbound(os.environ["DENNIS_USER"], os.environ["DENNIS_COMMAND"])
    time.sleep(0.2)
    for message in dbman.get_outbound(os.environ["DENNIS_USER"])["messages"]:
        print(message)
    dbman.reset_outbound(os.environ["DENNIS_USER"])
else:
    if "command" not in fields:
        pass
    else:
        if not dbman.get_inbound(os.environ["REMOTE_ADDR"]):
            dbman.reset_inbound(os.environ["REMOTE_ADDR"])
        if not dbman.get_outbound(os.environ["REMOTE_ADDR"]):
            dbman.reset_outbound(os.environ["REMOTE_ADDR"])
            dbman.append_inbound(os.environ["REMOTE_ADDR"], fields["command"])
        time.sleep(0.2)
        for message in dbman.get_outbound(os.environ["REMOTE_ADDR"])["messages"]:
            print(message)
        dbman.reset_outbound(os.environ["REMOTE_ADDR"])
