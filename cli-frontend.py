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


class Router:
    """Dummy Router
    """
    def __init__(self):
        self.users = {}
        self.shell = None
        self.single_user = True

    def message(self, peer, msg, _nbsp=None):
        pass

    def broadcast_all(self, msg, exclude=None):
        if not exclude:
            print(msg)

    def broadcast_room(self, room, msg, exclude=None):
        if not exclude:
            print(msg)


class Log:
    """Stand-in for Twisted's logger.
    """
    def debug(self, msg, **kwargs):
        print("[cli#debug]", msg.format(**kwargs))

    def info(self, msg, **kwargs):
        print("[cli#info]", msg.format(**kwargs))

    def warn(self, msg, **kwargs):
        print("[cli#warn]", msg.format(**kwargs))

    def error(self, msg, **kwargs):
        print("[cli#error]", msg.format(**kwargs))

    def critical(self, msg, **kwargs):
        print("[cli#critical]", msg.format(**kwargs))


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

    log = Log()

    # Initialize the database manager.
    log.info("initializing database manager")
    dbman = database.DatabaseManager(config["database"]["filename"], log)
    if not dbman._startup():
        return 3
    log.info("finished initializing database manager")

    # Initialize the router.
    router = Router()

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

    # Register us with the router.
    router.users["<world>"] = {"service": "cli-frontend", "console": dennis}

    print("You are now logged in as the administrative user \"<world>\".")

    # Command loop.
    while True:
        cmd = input("> ")
        if cmd == "quit":
            break
        if cmd == "debug":
            pdb.set_trace()
            continue
        print(command_shell.command(dennis, cmd))

    # Just before shutdown.
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
if __name__ == "__main__":
    sys.exit(main())
