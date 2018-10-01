#####################
# Dennis MUD        #
# irc-frontend.py   #
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

import blackbox
import console
import database
import json
import time


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

    def register(self, username, nickname):
        self.users[username] = console.Console(dbman, nickname, self)

    def message(self, nickname, msg):
        irc.say(nickname, msg)

    def broadcast_all(self, msg):
        for u in self.users:
            if not self.users[u].user:
                continue
            irc.say(self.users[u].rname, msg)

    def broadcast_room(self, room, msg):
        for u in self.users:
            if not self.users[u].user:
                continue
            if self.users[u].user.room == room:
                irc.say(self.users[u].rname, msg)


router = Router()


with open("irc.config.json") as f:
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

irc = blackbox.IRC()
parser = blackbox.Parser()
irc.connect(config["host"], config["port"])
irc.nickname(config["nickname"])
irc.username(config["username"], config["realname"])


def broadcast(msg):
    for r in router:
        irc.say(r[0], msg)


joined = False
while True:
    data = irc.recv()
    event = parser.parse(data)
    user = event.user()
    nick = event.origin()[1:]
    if joined is False and event.command == "376":
        for channel in config["channels"]:
            irc.join(channel)
            joined = True
    if user and event.command == "PRIVMSG":
        if user not in router:
            router.register(user, nick)
        if user in router:
            print(' '.join(event.params[1:]))
            router[user].command(' '.join(event.params[1:]))

    time.sleep(0.1)  # Don't waste CPU cycles.
