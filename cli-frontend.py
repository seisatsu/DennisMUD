#####################
# Dennis MUD        #
# cli-frontend.py   #
# Copyright 2018    #
# Michael D. Reiley #
#####################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

import pdb
import sys

# Check Python version.
if sys.version_info[0] != 3:
    print("exiting: Dennis requires Python 3")
    sys.exit(1)

import console
import database
import json


class Router:
    def __init__(self):
        pass

    def message(self, nickname, msg, _nbsp=None):
        pass

    def broadcast_all(self, msg):
        pass

    def broadcast_room(self, room, msg):
        pass


# Try to open the cli config file.
try:
    with open("cli.config.json") as f:
        config = json.load(f)
except:
    print("exiting: could not open cli.config.json")
    sys.exit(1)

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

print("Welcome to Dennis MUD single-user mode.")
print("Connected to database at \"{0}:{1}/{2}\".".format(config["database"]["host"], config["database"]["port"],
                                                    config["database"]["name"]))
print("You are now logged in as the administrative user \"<world>\".")

# Command loop.
while True:
    cmd = input("> ")
    if cmd == "quit":
        sys.exit(0)
    if cmd == "debug":
        pdb.set_trace()
        continue
    print(dennis.command(cmd))
