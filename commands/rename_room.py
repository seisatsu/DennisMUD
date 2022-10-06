#######################
# Dennis MUD          #
# rename_room.py      #
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

NAME = "rename room"
CATEGORIES = ["rooms"]
USAGE = "rename room <new_name>"
DESCRIPTION = """Set the name of the current room to <new_name>.

You must own the current room in order to rename it.
Wizards can rename any room.

Ex. `rename room Small Bedroom`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console, owner=True)
    if not thisroom:
        return False

    # Make sure the room name is not an integer, as this would be confusing.
    # We actually want an exception to be raised here.
    if len(args) == 1:
        try:
            int(args[0])
            console.msg("{0}: The room name cannot be an integer.".format(NAME))
            return False
        except ValueError:
            # Not an integer.
            pass

    # Get new room name.
    roomname = ' '.join(args)
    if roomname == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Make sure a room by this name does not already exist.
    # Make an exception if that is the room we are renaming. (changing case)
    for room in console.database.rooms.all():
        if room["name"].lower() == roomname.lower() and room["name"].lower() != thisroom["name"].lower():
            console.msg("{0}: A room by that name already exists.".format(NAME))
            return False

    # Rename the room.
    thisroom["name"] = roomname
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
