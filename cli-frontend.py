#####################
# Dennis MUD        #
# cli-frontend.py   #
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

import sys

# Check Python version.
if sys.version_info[0] != 3:
    print("Not Starting: Dennis requires Python 3")
    sys.exit(1)

import console
import database
import shell

import json
import pdb

from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory


class Router:
    """Dummy Router

    This provides just enough functionality for Dennis to run with one player.
    """
    def __init__(self, log):
        self.users = {}
        self.shell = None
        self.single_user = True
        self.log = log

    def message(self, peer, msg, _nbsp=None):
        pass

    def broadcast_all(self, msg, exclude=None):
        if not exclude:
            self.log.write(msg)

    def broadcast_room(self, room, msg, exclude=None):
        if not exclude:
            self.log.write(msg)


class Log:
    """Stand-in for Twisted's logger.

    Logs to STDOUT, and optionally to a file.
    Filters out unwanted messages using a log level setting.

    :ivar loglevel: The log level to use. One of "debug", "info", "warn", "error", "critical", in descending verbosity.
    :ivar logfile: The open file to log to.
    """
    def __init__(self, loglevel, logfile):
        self._loglevel = loglevel
        self._logfile = logfile

    def debug(self, msg, **kwargs):
        """Write a debug level message to the console and/or the log file.
        """
        if self._loglevel in ["debug"]:
            print("[cli#debug]", msg.format(**kwargs))
            if self._logfile:
                self._logfile.write("[cli#debug] " + msg.format(**kwargs) + "\n")

    def info(self, msg, **kwargs):
        """Write an info level message to the console and/or the log file.
        """
        if self._loglevel in ["debug", "info"]:
            print("[cli#info]", msg.format(**kwargs))
            if self._logfile:
                self._logfile.write("[cli#info] " + msg.format(**kwargs) + "\n")

    def warn(self, msg, **kwargs):
        """Write a warn level message to the console and/or the log file.
        """
        if self._loglevel in ["debug", "info", "warn"]:
            print("[cli#warn]", msg.format(**kwargs))
            if self._logfile:
                self._logfile.write("[cli#warn] " + msg.format(**kwargs) + "\n")

    def error(self, msg, **kwargs):
        """Write an error level message to the console and/or the log file.
        """
        if self._loglevel in ["debug", "info", "warn", "error"]:
            print("[cli#error]", msg.format(**kwargs))
            if self._logfile:
                self._logfile.write("[cli#error] " + msg.format(**kwargs) + "\n")

    def critical(self, msg, **kwargs):
        """Write a critical level message to the console and/or the log file.

        All log levels include critical, so these messages cannot be disabled.
        """
        print("[cli#critical]", msg.format(**kwargs))
        if self._logfile:
            self._logfile.write("[cli#critical] " + msg.format(**kwargs) + "\n")

    def write(self, msg):
        """Write an untagged message to the console and/or the log file, regardless of log level.
        """
        print(msg)
        self._logfile.write(str(msg) + "\n")


def main():
    print("Welcome to Dennis MUD PreAlpha, Single-User Client.")
    print("Starting up...")

    # Try to open the cli config file.
    try:
        with open("cli.config.json") as f:
            config = json.load(f)
    except:
        print("[cli#critical] could not open cli.config.json")
        return 2

    # Try to open the log file for writing, if one is set.
    # Otherwise don't use one.
    logfile = None
    if config["log"]["file"]:
        try:
            logfile = open(config["log"]["file"], 'a')
        except:
            if config["log"]["level"] in ["debug", "info", "warn"]:
                print("[cli#warn] Could not open cli log file: {0}".format(config["log"]["file"]))
    log = Log(config["log"]["level"], logfile)

    # Initialize the database manager.
    log.info("initializing database manager")
    dbman = database.DatabaseManager(config["database"]["filename"], log)
    if not dbman._startup():
        return 3
    log.info("finished initializing database manager")

    # Initialize the router.
    router = Router(log)

    # Initialize the command shell.
    command_shell = shell.Shell(dbman, router)
    router.shell = command_shell

    # Log in as the root user. Promote to wizard if it was somehow demoted.
    dennis = console.Console(router, command_shell, "<world>", dbman, log)
    dennis.user = dbman.user_by_name("<world>")
    dbman._users_online.append("<world>")
    if not dennis.user["wizard"]:
        dennis.user["wizard"] = True
        dbman.upsert_user(dennis.user)

    # Register our console with the router.
    router.users["<world>"] = {"service": "cli-frontend", "console": dennis}

    # Try to start a command prompt session with a history file.
    # Otherwise start a sessionless prompt without history.
    try:
        command_prompt = PromptSession(history=FileHistory(config["prompt"]["history"])).prompt
    except:
        command_prompt = prompt

    # Welcome!
    log.write("You are now logged in as the administrative user \"<world>\".")

    # Command loop.
    running = True
    while running:
        try:
            cmd = command_prompt("> ")
            if cmd == "quit":
                break
            if cmd == "debug":
                pdb.set_trace()
                continue
            log.write(command_shell.command(dennis, cmd))
        except KeyboardInterrupt:
            running = False

    # Just before shutdown.
    dbman._unlock()
    log.write("End Program.")
    return 0


# Don't do anything if we're not running as a program.
# Otherwise, run main() and return its exit status to the OS.
# Return Codes:
# * 0: Success.
# * 1: Wrong Python version.
# * 2: Could not read main configuration file.
# * 3: Could not initialize DatabaseManager.
if __name__ == "__main__":
    sys.exit(main())
