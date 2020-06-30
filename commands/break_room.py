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


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    roomid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if roomid is None:
        return False

    # Check if the room exists.
    targetroom = COMMON.check_room(NAME, console, roomid)
    if not targetroom:
        return False

    # Check that we own the room or are a wizard.
    if console.user["name"] not in targetroom["owners"] and not console.user["wizard"]:
        console.msg("{0}: you do not own this room".format(NAME))
        return False

    # Make sure the room is empty.
    if targetroom["users"]:
        console.msg("{0}: you cannot break an occupied room".format(NAME))
        return False

    # Remove this room from the entrances record of every room it has an exit to.
    for ex in targetroom["exits"]:
        destroom = console.database.room_by_id(ex["dest"])
        if targetroom["id"] in destroom["entrances"]:
            destroom["entrances"].remove(targetroom["id"])
            console.database.upsert_room(destroom)

    # Delete the room.
    console.database.delete_room(targetroom)

    # Finished.
    console.msg("{0}: done".format(NAME))
    return True


