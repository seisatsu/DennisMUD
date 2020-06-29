#####################
# Dennis MUD        #
# list_entrances.py #
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

NAME = "list entrances"
CATEGORIES = ["exits", "rooms"]
USAGE = "list entrances [room]"
DESCRIPTION = """List the entrances leading to a room.

If a room ID is provided as an optional argument, list the entrances to that room.
Otherwise, list the entrances to the room you are currently in.
You must be an owner of a room to list its entrances.

Ex. `list entrances` to list the entrances to the current room.
Ex. `list entrances 5` to list the entrances to the room with ID 5."""


def COMMAND(console, args):
    if len(args) > 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    if len(args) == 1:
        try:
            roomid = int(args[0])
            thisroom = console.database.room_by_id(roomid)
        except ValueError:
            console.msg("Usage: " + USAGE)
            return False
    else:
        thisroom = console.database.room_by_id(console.user["room"])

    # Check if the room exists.
    if not thisroom:
        console.msg(NAME + ": no such room")
        return False

    # Check that we own the room or are a wizard.
    if console.user["name"] not in thisroom["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this room")
        return False

    # Are there any entrances?
    if not thisroom["entrances"]:
        console.msg("this room has no entrances")
        return True

    # Enumerate exits leading to this one, and the rooms containing them.
    for ent in sorted(thisroom["entrances"]):
        srcroom = console.database.room_by_id(ent)
        if not srcroom:
            console.msg("warning: entrance room does not exist: {0}".format(ent))
            continue
        exits = []
        for ex in enumerate(srcroom["exits"]):
            if ex[1]["dest"] == thisroom["id"]:
                exits.append(ex)
        body = "{0} ({1}) :: ".format(srcroom["name"], srcroom["id"])
        for ex in exits:
            body += "{0} ({1}), ".format(ex[1]["name"], ex[0])
        body = body[:-2]
        console.msg(body)

    return True