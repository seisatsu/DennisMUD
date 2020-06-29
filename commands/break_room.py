#####################
# Dennis MUD        #
# break_room.py     #
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

NAME = "break room"
CATEGORIES = ["rooms"]
ALIASES = ["delete room", "destroy room", "remove room"]
USAGE = "break room <room>"
DESCRIPTION = """Break the room with ID <room> if you are its owner.

You must be an owner of the room, and no one can be in the room, including yourself.

Ex. `break room 5` to break the room with ID 5."""


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        roomid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    thisroom = database.room_by_id(roomid)

    # Check if the room exists.
    if not thisroom:
        console.msg(NAME + ": no such room")
        return False

    # Check that we own the room or are a wizard.
    if console.user["name"] not in thisroom["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this room")
        return False

    # Make sure the room is empty.
    if thisroom["users"]:
        console.msg(NAME + ": you cannot break an occupied room")
        return False

    # Remove this room from the entrances record of every room it has an exit to.
    for ex in thisroom["exits"]:
        destroom = database.room_by_id(ex["dest"])
        if thisroom["id"] in destroom["entrances"]:
            destroom["entrances"].remove(thisroom["id"])
            database.upsert_room(destroom)

    # Delete the room.
    database.delete_room(thisroom)

    console.msg(NAME + ": done")
    return True


