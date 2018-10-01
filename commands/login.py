#####################
# Dennis MUD        #
# login.py          #
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

import hashlib

NAME = "login"
CATEGORIES = ["users"]
USAGE = "login <username> <password>"
DESCRIPTION = "Log in as the user <username> if not currently logged in, using <password>."


def COMMAND(console, database, args):
    # args = [username, password]
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    if console.user:
        console.msg(NAME + ": already logged in")
        return False

    thisuser = database.users.find_one(
        {
            "name": args[0].lower(),
            "passhash": hashlib.sha256(args[1].encode()).hexdigest()
        }
    )
    if not thisuser:
        console.msg(NAME + ": bad credentials")
        return False  # Bad login.
    console.user = thisuser
    console.user["online"] = True
    database.upsert_user(console.user)

    # Look for the current room.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    # If we are not in the room, put us there.
    if not console.user["name"] in thisroom["users"]:
        thisroom["users"].append(console.user["name"])
        database.upsert_room(thisroom)

    console.msg("logged in as \"" + console.user["name"] + "\"")
    console.msg('=' * 20)
    console.broadcast_room(console.user["nick"] + " entered the dream")
    console.command("look", False)
    return True
