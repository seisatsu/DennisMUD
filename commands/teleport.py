#####################
# Dennis MUD        #
# teleport.py       #
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

NAME = "teleport"
CATEGORIES = ["exploration"]
ALIASES = ["tel", "tp"]
USAGE = "teleport <room>"
DESCRIPTION = """Teleport to the room with ID <room>.

Anyone can teleport to room 0, but otherwise you can only teleport to a room that you own.

Ex. `teleport 0` to go to the first room.
Ex2. `teleport 17` to go to room 17."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    destroomid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if destroomid is None:
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # Lookup the destination room and perform room checks.
    destroom = COMMON.check_room(NAME, console, destroomid)
    if not destroom:
        return False

    # Make sure we are the destination room owner or a wizard, or the destination is the first room.
    if not console.user["name"] in destroom["owners"] and not console.user["wizard"] and not destroom["id"] == 0:
        console.msg("{0}: You do not have permission to teleport to that room.".format(NAME))
        return False

    # Remove us from the current room.
    if console.user["name"] in thisroom["users"]:
        thisroom["users"].remove(console.user["name"])

    # Add us to the destination room.
    if console.user["name"] not in destroom["users"]:
        destroom["users"].append(console.user["name"])

    # If we are posturing on an item, it's not coming with us.
    console["posture_item"] = None

    # Broadcast our teleportation to the origin room.
    console.shell.broadcast_room(console, "{0} vanished from the room.".format(console.user["nick"]))

    # Set our current room to the new room.
    console.user["room"] = destroom["id"]

    # Broadcast our arrival to the destination room, but not to ourselves.
    console.shell.broadcast_room(console, "{0} entered the room.".format(console.user["nick"]),
                                 exclude=console.user["name"])

    # Save the origin room, the destination room, and our user document.
    console.database.upsert_room(thisroom)
    console.database.upsert_room(destroom)
    console.database.upsert_user(console.user)

    # Take a look around.
    console.shell.command(console, "look", False)

    # Finished.
    return True
