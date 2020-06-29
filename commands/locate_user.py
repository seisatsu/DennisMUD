#####################
# Dennis MUD        #
# locate_user.py    #
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

NAME = "locate user"
CATEGORIES = ["users"]
ALIASES = ["find user"]
USAGE = "locate user <name>"
DESCRIPTION = """Find out what room the user with username <name> is in.

This only works with usernames, not with nicknames.
See the `realname` command to derive a user's username from their nickname.
If a user is offline, only wizards can see their location.

Ex. `locate user seisatsu`"""


def COMMAND(console, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    u = console.database.user_by_name(args[0].lower())
    if not u:
        console.msg(NAME + ": no such user")
        return False

    # If the user is offline or we are a wizard, show their location.
    if console.database.online(u["name"]):
        for r in console.database.rooms.all():
            if u["name"] in r["users"]:
                console.msg("User " + u["name"] + " is in room " + r["name"] + " (" + str(r["id"]) + ")")
                return True
    elif console.user["wizard"]:
        console.msg("User " + u["name"] + " (offline) is in room " + str(u["room"]) + " (" + str(r["id"]) + ")")
        return True

    # User is not online and we are not a wizard.
    else:
        console.msg("User " + u["name"] + " is offline")
        return True

    # Couldn't find the user.
    console.msg(NAME + ": Warning: user is online but could not be found")
    return False
