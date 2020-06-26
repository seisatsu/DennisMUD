#####################
# Dennis MUD        #
# server.py         #
# Copyright 2020    #
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

# Parts of codebase borrowed from https://github.com/TKeesh/WebSocketChat

import sys

# Check Python version.
if sys.version_info[0] != 3:
    print("[server#error] exiting: Dennis requires Python 3")
    sys.exit(1)

import console
import database
import html
import json
import telnet
import websocket

from twisted.internet import reactor
from twisted.logger import Logger, textFileLogObserver, globalLogBeginner

# Try to read the server config file.
try:
    with open("server.config.json") as f:
        config = json.load(f)
except:
    print("[server#critical] exiting: could not open server.config.json")
    sys.exit(1)

# Initialize logging. At least one logging method is required.
if not config["log"]["stdout"] and not config["log"]["file"]:
    # No logging option is set, so force stdout.
    config["log"]["stdout"] = True
elif config["log"]["file"]:
    # Try to open the log file.
    try:
        logfile = open(config["log"]["file"], 'a')
    except:
        # Warn and fall back to STDOUT.
        print("[server#critical] warning: could not open log file:", config["log"]["file"])
        config["log"]["file"] = None
        config["log"]["stdout"] = True
# Configure log targets.
logtargets = []
if config["log"]["stdout"]:
    logtargets.append(textFileLogObserver(sys.stdout))
if config["log"]["file"]:
    logtargets.append(textFileLogObserver(logfile))
globalLogBeginner.beginLoggingTo(logtargets)
# Start the logger.
log = Logger("server")

# Open the Dennis main database.
dbman = database.DatabaseManager(config["database"]["filename"])

# Reset users.
rooms = dbman.rooms.all()
if len(rooms):
    for r in rooms:
        r["users"] = []
        dbman.upsert_room(r)
users = dbman.users.all()
if len(users):
    for u in users:
        u["online"] = False
        dbman.upsert_user(u)


class Router:
    """Router

    This class handles interfacing between the server backends and the user command consoles. It manages a lookup table
    of connected users and their consoles, and handles passing messages between them.

    Attributes:
        users: Dictionary of connected users and their consoles, as well as the protocols they are connected by.
        single_user: Whether we are running in single-user mode. Hard-coded here to False.
        telnet_factory: The active telnet server factory.
        websocket_factory: The active websocket server factory.
    """
    def __init__(self):
        """Router Initializer
        """
        self.users = {}
        self.single_user = False
        self.telnet_factory = None
        self.websocket_factory = None

    def __contains__(self, item):
        """__contains__

        Check if a peer name is present in the users table.

        :param item: Internal peer name.
        :return: True if succeeded, False if failed.
        """
        if item in self.users:
            return True
        return False

    def __getitem__(self, item):
        """__getitem__

        Get a user record by their peer name.

        :param item: Internal peer name.
        :return: User record if succeeded, None if failed.
        """
        if self.__contains__(item):
            return self.users[item]
        else:
            return None

    def __iter__(self):
        """__iter__
        """
        return self.users.items()

    def register(self, peer, service):
        """Register User

        :param peer: Internal peer name.
        :param service: Service type. "telnet" or "websocket".
        :return: True
        """
        self.users[peer] = {"service": service, "console": console.Console(dbman, peer, self)}
        self.users[peer]["console"]._disabled_commands = config["disabled"]
        return True

    def unregister(self, peer):
        """Unregister and Logout User

        :param peer: Internal peer name.
        :return: True if succeeded, False if no such user.
        """
        if peer not in self.users:
            return False
        if not self.users[peer]["console"].user:
            return False
        self.users[peer]["console"].command("logout")
        del self.users[peer]
        return True

    def message(self, peer, msg, _nbsp=False):
        """Message Peer

        Message a user by their internal peer name.

        :param peer: Internal peer name.
        :param msg: Message to send.
        :param _nbsp: Will insert non-breakable spaces for formatting on the websocket frontend.
        :return: True
        """
        if self.users[peer]["service"] == "telnet":
            self.telnet_factory.communicate(peer, msg.encode())
        if self.users[peer]["service"] == "websocket":
            self.websocket_factory.communicate(peer, html.escape(msg).encode("utf-8"), _nbsp)

    def broadcast_all(self, msg):
        """Broadcast All

        Broadcast a message to all logged in users.

        :param msg: Message to send.
        :return: True
        """
        for u in self.users:
            if not self.users[u]["console"].user:
                continue
            if self.users[u]["service"] == "telnet":
                self.telnet_factory.communicate(self.users[u]["console"].rname, msg.encode())
            if self.users[u]["service"] == "websocket":
                self.websocket_factory.communicate(self.users[u]["console"].rname, html.escape(msg).encode("utf-8"))

    def broadcast_room(self, room, msg):
        """Broadcast Room

        Broadcast a message to all logged in users in the given room.

        :param room: Room ID.
        :param msg: Message to send.
        :return: True
        """
        for u in self.users:
            if not self.users[u]["console"].user:
                continue
            if self.users[u]["console"].user["room"] == room:
                if self.users[u]["service"] == "telnet":
                    self.telnet_factory.communicate(self.users[u]["console"].rname, msg.encode())
                if self.users[u]["service"] == "websocket":
                    self.websocket_factory.communicate(self.users[u]["console"].rname, html.escape(msg).encode("utf-8"))


if __name__ == "__main__":
    """Main Program
    """
    # Create the router instance we will use.
    router = Router()

    # We will exit if no services are enabled.
    any_enabled = False

    # If telnet is enabled, initialize its service.
    if config["telnet"]["enabled"]:
        telnet_factory = telnet.ServerFactory(router)
        reactor.listenTCP(config["telnet"]["port"], telnet_factory)
        any_enabled = True

    # If websocket is enabled, initialize its service.
    if config["websocket"]["enabled"]:
        if config["websocket"]["secure"]:
            # Use secure websockets. Generally requires HTTPS for the client page. TODO: Fix.
            websocket_factory = websocket.ServerFactory(router, "wss://" + config["websocket"]["host"] + ":" +
                                                        str(config["websocket"]["port"]))
        else:
            # Use insecure websockets.
            websocket_factory = websocket.ServerFactory(router, "ws://" + config["websocket"]["host"] + ":" +
                                                        str(config["websocket"]["port"]))
        websocket_factory.protocol = websocket.ServerProtocol
        websocket_factory.setProtocolOptions(autoPingInterval=1, autoPingTimeout=3, autoPingSize=20)
        reactor.listenTCP(config["websocket"]["port"], websocket_factory)
        any_enabled = True

    if not any_enabled:
        # No services were enabled.
        log.critical("exiting: no services enabled")
        dbman._unlock()
        sys.exit(1)

    # Start the Twisted Reactor.
    reactor.run()

    # Just before shutdown.
    dbman._unlock()
    log.info("end program", log_source="test")
