#####################
# Dennis MUD        #
# xyzzy.py          #
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

NAME = "xyzzy"
CATEGORIES = ["exploration"]
USAGE = "xyzzy"
DESCRIPTION = """Teleport back to the first room.

Anyone can use this command to teleport to room 0.
It is functionally the same as using `teleport 0`.

Ex. `xyzzy` to go to the first room."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # Lookup the first room and perform room checks.
    destroom = COMMON.check_room(NAME, console, 0)
    if not destroom:
        return False

    # Remove us from the current room.
    if console.user["name"] in thisroom["users"]:
        thisroom["users"].remove(console.user["name"])

    # Add us to the destination room.
    if console.user["name"] not in destroom["users"]:
        destroom["users"].append(console.user["name"])

    # Broadcast our teleportation to the origin room.
    console.shell.broadcast_room(
        console, "{0} uttered a mysterious word and vanished from the room.".format(console.user["nick"]))

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
