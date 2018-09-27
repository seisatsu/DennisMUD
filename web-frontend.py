import blitzdb
import cgi
import json
import os
import time
from datatype import Exchange

# Use IP address for routing!

# Read the config file.
with open("web.config.json") as f:
    config = json.load(f)

# Retrieve HTTP request fields.
fields = cgi.FieldStorage()

# Open the BlitzDB data exchange database.
database = blitzdb.FileBackend(config["exchange"])

# If the exchange document does not exist, fail. The backend is not ready.
exchange = database.filter(Exchange, {})
if len(exchange) == 0:
    print("NOT READY")

else:
    exchange = exchange[0]

if "DENNIS_TESTCLIENT" in os.environ:
    if os.environ["DENNIS_USER"] not in exchange.inbound:
        exchange.inbound[os.environ["DENNIS_USER"]] = []
    if os.environ["DENNIS_USER"] not in exchange.outbound:
        exchange.outbound[os.environ["DENNIS_USER"]] = []
    exchange.inbound[os.environ["DENNIS_USER"]].append(os.environ["DENNIS_COMMAND"])
    exchange.save()
    database.commit()
    time.sleep(0.2)
    for message in exchange.inbound[os.environ["DENNIS_USER"]]:
        print(message)
else:
    if "command" not in fields:
        pass
    else:
        if os.environ["REMOTE_ADDR"] not in exchange.inbound:
            exchange.inbound[os.environ["REMOTE_ADDR"]] = []
        if os.environ["REMOTE_ADDR"] not in exchange.outbound:
            exchange.outbound[os.environ["REMOTE_ADDR"]] = []
        exchange.inbound[os.environ["REMOTE_ADDR"]].append(fields["command"])
        exchange.save()
        database.commit()
        time.sleep(0.2)
    for message in exchange.outbound[os.environ["REMOTE_ADDR"]]:
        print(message)
