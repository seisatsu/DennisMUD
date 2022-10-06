#######################
# Dennis MUD          #
# make_exit.py        #
# Copyright 2018-2020 #
# Sei Satzparad       #
#######################

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

NAME = "make exit"
CATEGORIES = ["exits"]
ALIASES = ["create exit", "new exit"]
USAGE = "make exit <destination> <exit_name>"
DESCRIPTION = """Create a new exit called <exit_name> in the current room, leading to the room with ID <destination>.

The current room must not be outbound sealed, and the destination room must not be inbound sealed.
These restrictions do not apply to the owner of the current room and the owner of the destination room, respectively.
You will be added as an owner of the new exit.
Wizards can create an exit to anywhere in any room.

Ex. `make exit 12 Iron Door` to make an exit in the current room called "Iron Door" leading to room 12."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2):
        return False

    # Perform argument type checks and casts.
    destroomid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if destroomid is None:
        return False

    # Make sure the exit name is not an integer, as this would be confusing.
    # We actually want an exception to be raised here.
    if len(args) == 2:
        try:
            int(args[1])
            console.msg("{0}: Exit name cannot be an integer.".format(NAME))
            return False
        except ValueError:
            # Not an integer.
            pass

    # Get exit name.
    exitname = ' '.join(args[1:])
    if exitname == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # Make sure an exit by this name does not already exist in the current room.
    exits = thisroom["exits"]
    for ex in exits:
        if ex["name"].lower() == exitname.lower():
            console.msg("{0}: An exit by this name already exists in this room.".format(NAME))
            return False

    # Lookup the destination room and perform room checks.
    destroom = COMMON.check_room(NAME, console, destroomid)
    if not destroom:
        return False

    # Make sure the current room is not outbound sealed, or we are a room owner or a wizard.
    if thisroom["sealed"]["outbound"] and not console.user["wizard"] and console.user["name"] not in thisroom["owners"]:
        console.msg("{0}: The current room is outbound sealed.".format(NAME))
        return False

    # Make sure the destination room is not inbound sealed, or we are a room owner or a wizard.
    if destroom["sealed"]["inbound"] and not console.user["wizard"] and console.user["name"] not in destroom["owners"]:
        console.msg("{0}: The destination room is inbound sealed.".format(NAME))
        return False

    # Create our new exit and add it to the current room.
    newexit = {
        "dest": destroomid,
        "name": exitname,
        "desc": "",
        "owners": [console.user["name"]],
        "key": None,
        "key_hidden": False,
        "locked": False,
        "action": {
            "go": "",
            "locked": "",
            "entrance": ""
        }
    }
    thisroom["exits"].append(newexit)
    console.database.upsert_room(thisroom)

    # If this room is not in the entrance list for the destination room, add it.
    if console.user["room"] not in destroom["entrances"]:
        destroom["entrances"].append(console.user["room"])
        console.database.upsert_room(destroom)

    # Show the exit ID.
    console.msg("{0}: Done. (exit id: {1})".format(NAME, len(thisroom["exits"])-1))
    return True
