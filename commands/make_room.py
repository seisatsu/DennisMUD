#####################
# Dennis MUD        #
# make_room.py      #
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

NAME = "make room"
CATEGORIES = ["rooms"]
ALIASES = ["create room", "new room"]
USAGE = "make room <name>"
DESCRIPTION = """Create a new room called <name>.

You will be added as an owner of the new room.

Ex. `make room Small Bedroom`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Make sure the room name is not an integer, as this would be confusing.
    # We actually want an exception to be raised here.
    if len(args) == 1:
        try:
            int(args[0])
            console.msg("{0}: Room name cannot be an integer.".format(NAME))
            return False
        except ValueError:
            # Not an integer.
            pass

    # Get room name.
    roomname = ' '.join(args)
    if roomname == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Get a list of all rooms, sorted in reverse order.
    allrooms = sorted(console.database.rooms.all(), reverse=True, key=lambda k: k["id"])

    # Make sure a room by this name does not already exist.
    for room in allrooms:
        if room["name"].lower() == roomname.lower():
            console.msg("{0}: A room by this name already exists.".format(NAME))
            return False

    # Find the highest numbered currently existing room ID.
    if allrooms:
        lastroom = allrooms[0]["id"]
    else:
        lastroom = -1

    # Create our new room with an ID one higher than the last room, and save the room.
    newroom = {
        "id": lastroom + 1,
        "name": roomname,
        "desc": "",
        "owners": [console.user["name"]],
        "users": [],
        "exits": [],
        "entrances": [],
        "items": [],
        "sealed": {
            "inbound": console.database.defaults["rooms"]["sealed"]["inbound"],
            "outbound": console.database.defaults["rooms"]["sealed"]["outbound"]
        }
    }
    console.database.upsert_room(newroom)

    # Show the room ID.
    console.msg("{0}: Done. (room id: {1})".format(NAME, newroom["id"]))
    return True
