########################
# Dennis MUD           #
# telnet-backend.py    #
# Copyright 2018       #
# Michael D. Reiley    #
########################

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

# Parts of codebase borrowed from https://github.com/TKeesh/WebSocketChat

import console
import database
import html
import json
import sys
import websocket
import telnet

from twisted.python import log
from twisted.internet import reactor

# Read the config file.
with open("server.config.json") as f:
    config = json.load(f)

# Open the Dennis main database.
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


class Router:
    def __init__(self):
        self.users = {}
        self.telnet_factory = None
        self.websocket_factory = None

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

    def register(self, peer, service):
        print(peer)
        self.users[peer] = [service, console.Console(dbman, peer, self)]

    def unregister(self, peer):
        self.users[peer][1].command("logout")
        del self.users[peer]

    def message(self, peer, msg):
        if users[peer][0] == "telnet":
            self.telnet_factory.communicate(peer, msg.encode())
        if users[peer][0] == "websocket":
            self.websocket_factory.communicate(peer, html.escape(msg).encode("utf-8"))

    def broadcast_all(self, msg):
        for u in self.users:
            if not self.users[u][1].user:
                continue
            if self.users[u][0] == "telnet":
                self.telnet_factory.communicate(self.users[u][1].rname, msg.encode())
            if self.users[u][0] == "websocket":
                self.websocket_factory.communicate(self.users[u][1].rname, html.escape(msg).encode("utf-8"))

    def broadcast_room(self, room, msg):
        for u in self.users:
            if not self.users[u][1].user:
                continue
            if self.users[u][1].user["room"] == room:
                if self.users[u][0] == "telnet":
                    self.telnet_factory.communicate(self.users[u][1].rname, msg.encode())
                if self.users[u][0] == "websocket":
                    self.websocket_factory.communicate(self.users[u][1].rname, html.escape(msg).encode("utf-8"))


if __name__ == "__main__":
    router = Router()

    log.startLogging(sys.stdout)

    any_enabled = False

    if config["telnet"]["enabled"]:
        telnet_factory = telnet.ServerFactory(router)
        reactor.listenTCP(config["telnet"]["port"], telnet_factory)
        any_enabled = True

    if config["websocket"]["enabled"]:
        if config["websocket"]["secure"]:
            websocket_factory = websocket.ServerFactory(router, "wss://" + config["websocket"]["host"] + ":" +
                                                        str(config["websocket"]["port"]))
        else:
            websocket_factory = websocket.ServerFactory(router, "ws://" + config["websocket"]["host"] + ":" +
                                                        str(config["websocket"]["port"]))
        websocket_factory.protocol = websocket.ServerProtocol
        reactor.listenTCP(config["websocket"]["port"], websocket_factory)
        any_enabled = True

    if not any_enabled:
        print("Exiting: no services enabled.")
        sys.exit(1)

    reactor.run()
