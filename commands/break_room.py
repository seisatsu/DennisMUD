#####################
# Dennis MUD        #
# break_room.py     #
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

NAME = "break room"
CATEGORIES = ["rooms"]
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

    # Check if the room exists.
    r = database.room_by_id(roomid)
    if r:
        # Check that we own the room.
        if console.user["name"] in r["owners"] or console.user["wizard"]:
            # Make sure the room is empty.
            if r["users"]:
                console.msg(NAME + ": you cannot break an occupied room")
                return False

            # Delete the room.
            database.delete_room(r)

            console.msg(NAME + ": done")
            return True

        # We don't own this room.
        console.msg(NAME + ": you do not own this room")
        return False

    # No room with that ID exists.
    console.msg(NAME + ": no such room")
    return False
