#######################
# Dennis MUD          #
# server.py           #
# Copyright 2018-2021 #
# Sei Satzparad       #
#######################

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
    print("Not Starting: Dennis requires Python 3.")
    sys.exit(1)

from lib import config as _config
from lib import console
from lib import database
from lib import logger
from lib import shell
from lib import telnet
from lib import websocket

import builtins
import html
import os
import shutil
import signal
import traceback

from datetime import datetime
from twisted.internet import reactor, ssl
from OpenSSL import crypto as openssl


class Router:
    """Router

    This class handles interfacing between the server backends and the user command consoles. It manages a lookup table
    of connected users and their consoles, and handles passing messages between them.

    :ivar users: Dictionary of connected users and their consoles, as well as the protocols they are connected by.
    :ivar shell: The shell instance, which handles commands and help.
    :ivar single_user: Whether we are running in single-user mode. Hard-coded here to False.
    :ivar telnet_factory: The active Autobahn telnet server factory.
    :ivar websocket_factory: The active Autobahn websocket server factory.
    :ivar shutting_down: Whether the server is currently counting down to shutdown.
    """
    def __init__(self, config, database):
        """Router Initializer

        :param config: The server configuration file.
        :param database: The DatabaseManager instance to use.
        """
        self.users = {}
        self.shell = None
        self.single_user = False
        self.telnet_factory = None
        self.websocket_factory = None
        self.shutting_down = False

        self._config = config
        self._database = database
        self._reactor = None

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

    def broadcast_all(self, msg, exclude=None):
        """Broadcast All

        Broadcast a message to all logged in users.

        :param msg: Message to send.
        :param exclude: If set, username to exclude from broadcast.

        :return: True
        """
        for u in self.users:
            if not self.users[u]["console"].user:
                continue
            if self.users[u]["console"].user["name"] == exclude:
                continue
            if self.users[u]["service"] == "telnet":
                self.telnet_factory.communicate(self.users[u]["console"].rname, msg.encode())
            if self.users[u]["service"] == "websocket":
                self.websocket_factory.communicate(self.users[u]["console"].rname, html.escape(msg).encode("utf-8"))

    def broadcast_room(self, room, msg, exclude=None):
        """Broadcast Room

        Broadcast a message to all logged in users in the given room.

        :param room: Room ID.
        :param msg: Message to send.
        :param exclude: If set, username to exclude from broadcast.

        :return: True
        """
        for u in self.users:
            if not self.users[u]["console"].user:
                continue
            if self.users[u]["console"].user["name"] == exclude:
                continue
            if self.users[u]["console"].user["room"] == room:
                if self.users[u]["service"] == "telnet":
                    self.telnet_factory.communicate(self.users[u]["console"].rname, msg.encode())
                if self.users[u]["service"] == "websocket":
                    self.websocket_factory.communicate(self.users[u]["console"].rname, html.escape(msg).encode("utf-8"))


def init_services(config, router, log):
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
            # Use secure websockets. Requires the key and certificate.
            # First we test the expiration date of the cert.
            # Thanks to https://kyle.io/2016/01/checking-a-ssl-certificates-expiry-date-with-python
            try:
                with open(config["websocket"]["cert"], "r") as f:
                    cert = openssl.load_certificate(openssl.FILETYPE_PEM, f.read().encode())
                    if datetime.strptime(cert.get_notAfter().decode("ascii"), "%Y%m%d%H%M%SZ") < datetime.now():
                        log.critical("Expired ssl certificate: {filename}", filename=config["websocket"]["cert"])
                        return False

            # Could not open the certificate.
            except:
                log.critical("Could not open ssl certificate: {filename}", filename=config["websocket"]["cert"])
                log.critical(traceback.format_exc(1))
                return False

            # Initialize secure websockets.
            websocket_factory = websocket.ServerFactory(router, "wss://" + config["websocket"]["host"] + ":" +
                                                        str(config["websocket"]["port"]))
            ssl_factory = ssl.DefaultOpenSSLContextFactory(config["websocket"]["key"], config["websocket"]["cert"])
        else:
            # Use insecure websockets.
            websocket_factory = websocket.ServerFactory(router, "ws://" + config["websocket"]["host"] + ":" +
                                                        str(config["websocket"]["port"]))

        # Set up protocol options.
        websocket_factory.protocol = websocket.ServerProtocol
        websocket_factory.setProtocolOptions(autoPingInterval=1, autoPingTimeout=3, autoPingSize=20)

        # Begin listening on SSL or plain TCP.
        if config["websocket"]["secure"]:
            reactor.listenSSL(config["websocket"]["port"], websocket_factory, ssl_factory)
        else:
            reactor.listenTCP(config["websocket"]["port"], websocket_factory)
        any_enabled = True

    # No services were enabled.
    if not any_enabled:
        log.critical("No services enabled.")
        return False

    # Finished.
    return True


def main():
    """Startup tasks, mainloop entry, and shutdown tasks.
    """
    # Load the configuration.
    config = _config.ConfigManager(single=False)
    builtins.CONFIG = config

    print("Welcome to {0}, Multi-Player Server.".format(_config.VERSION))
    print("Starting up...")

    # Initialize the logger.
    logger.init(config)
    log = logger.Logger("server")

    # Rotate database backups, if enabled.
    # Unfortunately this has to be done before loading the database, because Windows.
    if os.path.exists(config["database"]["filename"]):
        try:
            if config["database"]["backups"]:
                backupnumbers = sorted(range(1, config["database"]["backups"]), reverse=True)
                for bn in backupnumbers:
                    if os.path.exists("{0}.bk{1}".format(config["database"]["filename"], bn)):
                        shutil.copyfile("{0}.bk{1}".format(config["database"]["filename"], bn),
                                        "{0}.bk{1}".format(config["database"]["filename"], bn + 1))
                shutil.copyfile(config["database"]["filename"], "{0}.bk1".format(config["database"]["filename"]))
        except:
            log.error("Could not finish rotating backups for database: {file}", file=config["database"]["filename"])
            log.error(traceback.format_exc(1))

    # Initialize the Database Manager and load the world database.
    log.info("Initializing database manager...")
    dbman = database.DatabaseManager(config["database"]["filename"], config.defaults)
    _dbres = dbman._startup()
    if not _dbres:
        # On failure, only remove the lockfile if its existence wasn't the cause.
        if _dbres is not None:
            dbman._unlock()
        return 3
    log.info("Finished initializing database manager.")

    # Initialize the router.
    router = Router(config, dbman)

    # initialize the command shell.
    command_shell = shell.Shell(dbman, router)
    router.shell = command_shell

    # Start the services.
    log.info("Initializing services...")
    if not init_services(config, router, log):
        dbman._unlock()
        return 4
    log.info("Finished initializing services.")

    # Graceful shutdown on SIGINT (ctrl-c).
    # The shutdown command does the same thing.
    # To shut down quickly but cleanly, send the TERM signal.
    def shutdown(signal_received, frame):
        if not router.shutting_down:
            if config["shutdown_delay"]:
                command_shell.broadcast("<<<DENNIS IS SHUTTING DOWN IN {0} SECONDS>>>".format(config["shutdown_delay"]))
            else:
                command_shell.broadcast("<<<DENNIS IS SHUTTING DOWN>>>")
            reactor.callLater(config["shutdown_delay"], reactor.stop)
            router.shutting_down = True
    signal.signal(signal.SIGINT, shutdown)

    # Graceful immediate shutdown on SIGQUIT (ctrl-\).
    # Unlike SIGINT, this skips the shutdown timer and stops right away.
    def shutdown_now(signal_received, frame):
        reactor.stop()
    signal.signal(signal.SIGQUIT, shutdown_now)

    # Start the Twisted Reactor.
    log.info("Finished startup tasks.")
    router._reactor = reactor
    reactor.run()

    # Shutting down.
    dbman._unlock()
    print("End Program.")
    return 0


# Don't do anything if we're not running as a program.
# Otherwise, run main() and return its exit status to the OS.
# Return Codes:
# * 0: Success.
# * 1: Wrong Python version.
# * 2: Could not read main configuration file.
# * 3: Could not initialize DatabaseManager.
# * 4: Could not initialize services.
if __name__ == "__main__":
    sys.exit(main())
