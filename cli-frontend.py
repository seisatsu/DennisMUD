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

import console
import database
import json
import sys


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

# Command loop.
while True:
    cmd = input("> ")
    if cmd == "quit":
        sys.exit(0)
    print(dennis.command(cmd))
