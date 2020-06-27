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
USAGE = "make room <name>"
DESCRIPTION = """Create a new room called <name>.

You will be added as an owner of the new room.

Ex. `make room Small Bedroom`"""


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Get name.
    name = ' '.join(args)

    # Make sure the name is not an integer, as this would be confusing.
    try:
        test = int(name)
        console.msg(NAME + ": room name cannot be an integer")
        return False
    except ValueError:
        # Not an integer.
        pass

    # Check if a room by this name already exists. Case insensitive.
    rooms = sorted(database.rooms.all(), reverse=True, key=lambda k: k["id"])
    if rooms:
        for r in rooms:
            if r["name"].lower() == name.lower():
                console.msg(NAME + ": a room by this name already exists")
                return False  # A room by this name already exists.

    # Find the highest numbered currently existing room ID.
    if rooms:
        lastroom = rooms[0]["id"]
    else:
        lastroom = -1

    # Create our new room with an ID one higher.
    newroom = {
        "owners": [console.user["name"]],
        "id": lastroom + 1,
        "name": name,
        "desc": "",
        "users": [],
        "exits": [],
        "entrances": [],
        "items": [],
        "sealed": {
            "inbound": database.defaults["rooms"]["sealed"]["inbound"],
            "outbound": database.defaults["rooms"]["sealed"]["outbound"]
        }
    }

    # Save.
    database.upsert_room(newroom)
    console.msg(NAME + ": done (id: " + str(newroom["id"]) + ")")
    return True
