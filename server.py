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
    print("Not Starting: Dennis requires Python 3")
    sys.exit(1)

import console
import database
import shell

import html
import json
import telnet
import websocket

from twisted.internet import reactor, ssl
from twisted.logger import Logger, LogLevel, LogLevelFilterPredicate, \
    textFileLogObserver, FilteringLogObserver, globalLogBeginner


class Router:
    """Router

    This class handles interfacing between the server backends and the user command consoles. It manages a lookup table
    of connected users and their consoles, and handles passing messages between them.

    :ivar users: Dictionary of connected users and their consoles, as well as the protocols they are connected by.
    :ivar shell: The shell instance, which handles commands and help.
    :ivar single_user: Whether we are running in single-user mode. Hard-coded here to False.
    :ivar telnet_factory: The active Autobahn telnet server factory.
    :ivar websocket_factory: The active Autobahn websocket server factory.
    """
    def __init__(self, config, database):
        """Router Initializer
        """
        self.users = {}
        self.shell = None
        self.single_user = False
        self.telnet_factory = None
        self.websocket_factory = None

        self._config = config
        self._database = database

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
        self.users[peer] = {"service": service, "console": console.Console(self, self.shell, peer, self._database)}
        self.shell._disabled_commands = self._config["disabled"]
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
        self.shell.command(self.users[peer]["console"], "logout")
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


def init_logger(config):
    """Initialize the Twisted Logger
    """
    # Read log options from the server config. At least one logging method is required.
    if not config["log"]["stdout"] and not config["log"]["file"]:
        # No logging option is set, so force stdout.
        config["log"]["stdout"] = True
    elif config["log"]["file"]:
        # Try to open the log file.
        try:
            logfile = open(config["log"]["file"], 'a')
        except:
            # Couldn't open the log file, so warn and fall back to STDOUT.
            if config["log"]["level"] in ("warn", "info", "debug"):
                print("[server#warn] could not open log file:", config["log"]["file"])
            config["log"]["file"] = None
            config["log"]["stdout"] = True

    # Make sure the chosen log level is valid. Otherwise force the highest log level.
    if config["log"]["level"] not in ("critical", "error", "warn", "info", "debug"):
        print("[server#warn] invalid log level in config, defaulting to \"debug\"")
        config["log"]["level"] = "debug"

    # Configure the Twisted Logger targets.
    # (Thanks to https://stackoverflow.com/a/46651223/213445 and https://stackoverflow.com/a/49111089/213445)
    # This part took a while to figure out, so I'm documenting it here in detail.
    # The variable "logtargets" is a list of FilteringLogObserver instances.
    # Each FilteringLogObserver wraps a textFileLogObserver, and imposes a LogLevelFilterPredicate.
    # The textFileLogObserver writes to STDOUT or the file we opened earlier. So, there can be one or two of them.
    # The LogLevelFilterPredicate conveys a maximum LogLevel to FilteringLogObserver through the "predicates" argument.
    # The "predicates" argument to FilteringLogObserver must be iterable, so we wrap LogLevelFilterPredicate in a list.
    # At the end, we pass our "logtargets" list to globalLogBeginner.beginLoggingTo.
    # All future Twisted Logger instances will point to both of our log targets.
    # We can have multiple instances of Logger, one for each subsystem of Dennis,
    # and for each one we give it a single argument, which is the namespace for log lines from that subsystem.
    logtargets = []
    if config["log"]["stdout"]:
        logtargets.append(
            FilteringLogObserver(
                textFileLogObserver(sys.stdout),
                predicates=[LogLevelFilterPredicate(getattr(LogLevel, config["log"]["level"]))]
            )
        )
    if config["log"]["file"]:
        logtargets.append(
            FilteringLogObserver(
                textFileLogObserver(logfile),
                predicates=[LogLevelFilterPredicate(getattr(LogLevel, config["log"]["level"]))]
            )
        )
    globalLogBeginner.beginLoggingTo(logtargets)


def init_services(config, dbman, router, log):
    """Initialize the Telnet and/or WebSocket Services
    """
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
            # Use secure websockets.
            websocket_factory = websocket.ServerFactory(router, "wss://" + config["websocket"]["host"] + ":" +
                                                        str(config["websocket"]["port"]))
            ssl_factory = ssl.DefaultOpenSSLContextFactory(config["websocket"]["key"], config["websocket"]["cert"])
        else:
            # Use insecure websockets.
            websocket_factory = websocket.ServerFactory(router, "ws://" + config["websocket"]["host"] + ":" +
                                                        str(config["websocket"]["port"]))
        websocket_factory.protocol = websocket.ServerProtocol
        websocket_factory.setProtocolOptions(autoPingInterval=1, autoPingTimeout=3, autoPingSize=20)
        if config["websocket"]["secure"]:
            reactor.listenSSL(config["websocket"]["port"], websocket_factory, ssl_factory)
        else:
            reactor.listenTCP(config["websocket"]["port"], websocket_factory)
        any_enabled = True

    if not any_enabled:
        # No services were enabled.
        log.critical("no services enabled")
        return False
    return True


def main():
    """Startup tasks, mainloop entry, and shutdown tasks.
    """
    print("Welcome to Dennis MUD PreAlpha, Multi-User Server.")
    print("Starting up...")

    # Try to read the server config file.
    try:
        with open("server.config.json") as f:
            config = json.load(f)
    except:
        print("[server#critical] could not open server.config.json")
        return 1

    # Initialize the logger.
    stdout = sys.stdout
    if config["log"]["level"] in ("info", "debug"):
        print("[server#info] initializing logger")
    init_logger(config)
    log = Logger("server")
    log.info("finished initializing logger")

    # Initialize the Database Manager and load the world database.
    log.info("initializing database manager")
    dbman = database.DatabaseManager(config["database"]["filename"])
    _dbres = dbman._startup()
    if not _dbres:
        # On failure, only remove the lockfile if its existence wasn't the cause.
        if _dbres is not None:
            dbman._unlock()
        return 1
    log.info("finished initializing database manager")

    # Initialize the router.
    router = Router(config, dbman)

    # initialize the command shell.
    command_shell = shell.Shell(dbman, router)
    router.shell = command_shell

    # Start the services.
    log.info("initializing services")
    if not init_services(config, dbman, router, log):
        dbman._unlock()
        return 1
    log.info("finished initializing services")

    # Start the Twisted Reactor.
    log.info("finished startup tasks")
    reactor.run()

    # Shutting down.
    dbman._unlock()
    sys.stdout = stdout
    print("End Program.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
