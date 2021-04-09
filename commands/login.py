#######################
# Dennis MUD          #
# login.py            #
# Copyright 2018-2020 #
# Michael D. Reiley   #
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

import hashlib

NAME = "login"
CATEGORIES = ["users"]
USAGE = "login <username> <password>"
DESCRIPTION = """Log in as the user <username> if not currently logged in, using <password>.

First you must have registered a user with the `register` command.

Ex. `login myusername mypassword`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=2, online=False):
        return False

    # Make sure we are not already logged in.
    if console.user:
        console.msg("{0}: You are already logged in.".format(NAME))
        return False

    # Make sure we aren't getting brute forced.
    if console._login_delay:
        console.msg("{0}: Wait a second before trying again.".format(NAME))
        return False

    # Attempt to authenticate with the database.
    thisuser = console.database.login_user(args[0].lower(), hashlib.sha256(args[1].encode()).hexdigest())
    if not thisuser:
        console.msg("{0}: Incorrect username or password.".format(NAME))
        console._login_delay = True
        console.router._reactor.callLater(1, console._reset_login_delay)
        return False  # Bad login.
    console.user = thisuser

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # If we are not in the room, put us there.
    if not console.user["name"] in thisroom["users"]:
        thisroom["users"].append(console.user["name"])
        console.database.upsert_room(thisroom)

    # Update console's exit list.
    console.exits = []
    for exi in range(len(thisroom["exits"])):
        console.exits.append(thisroom["exits"][exi]["name"])

    # Show the log in message, broadcast our presence, and look at the room.
    console.msg("You are logged in as \"{0}\".".format(console.user["name"]))
    console.msg('=' * 20)
    console.shell.broadcast_room(console, "{0} logged in.".format(console.user["nick"]))
    console.shell.command(console, "look", False)
    return True
