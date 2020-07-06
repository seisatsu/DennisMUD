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
You must be an owner of the room to list its entrances.

Ex. `list entrances` to list the entrances to the current room.
Ex. `list entrances 5` to list the entrances to the room with ID 5."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Select the given room or the current room.
    if len(args) == 1:
        # Perform argument type checks and casts.
        roomid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
        if roomid is None:
            return False
    else:
        roomid = console.user["room"]

    # Lookup the target room and perform room checks.
    targetroom = COMMON.check_room(NAME, console, roomid, owner=True)
    if not targetroom:
        return False

    # Are there any entrances?
    if not targetroom["entrances"]:
        console.msg("{0}: This room has no entrances.".format(NAME))
        return True

    # Scan the entrance source rooms listed for this room.
    entcount = 0
    for ent in sorted(targetroom["entrances"]):
        # Lookup the entrance source room and perform room checks.
        srcroom = COMMON.check_room(NAME, console, ent, reason=False)
        if not srcroom:
            console.log.error("Entrance source room does not exist for target room: {srcroom} -> {targetroom}",
                              srcroom=ent, targetroom=roomid)
            console.msg("{0}: ERROR: Entrance room does not exist: {0}".format(NAME, ent))
            continue

        # Enumerate the exits in the entrance source room.
        exits = []
        for ex in enumerate(srcroom["exits"]):
            if ex[1]["dest"] == targetroom["id"]:
                exits.append(ex)

        # Format the entrance source room name and ID.
        body = "{0} ({1}) :: ".format(srcroom["name"], srcroom["id"])

        # Format the names and IDs of the exits in the entrance source room that lead to this room.
        for ex in exits:
            body += "{0} ({1}), ".format(ex[1]["name"], ex[0])

        # Trim extra ', ' from the end of the line and send it.
        body = body[:-2]
        console.msg(body)

        # Keep count.
        entcount += 1

    # Finished
    if not entcount:
        console.msg("{0}: This room has no entrances.".format(NAME))
    else:
        console.msg("{0}: Total entrances: {1}".format(NAME, entcount))
    return True
