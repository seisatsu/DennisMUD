######################
# Dennis MUD         #
# purge_entrances.py #
# Copyright 2021     #
# Sei Satzparad      #
######################

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

NAME = "purge entrances"
CATEGORIES = ["exits"]
USAGE = "purge entrances"
DESCRIPTION = """Break all exits in other rooms leading to the current room.

You must own the room in order to purge its entrances.
Wizards can purge the entrances from any room.

Ex. `purge entrances` to break every entrance to the current room."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console, owner=True)
    if not thisroom:
        return False

    # Make sure this room has any entrances.
    if not thisroom["entrances"]:
        console.msg("{0}: This room has no entrances.".format(NAME))
        return False

    # Scan the entrance source rooms listed for this room.
    entcount = 0
    for ent in sorted(thisroom["entrances"]):
        # Lookup the entrance source room and perform room checks.
        srcroom = COMMON.check_room(NAME, console, ent, reason=False)
        if not srcroom:
            console.log.error("Entrance source room does not exist for target room: {srcroom} -> {targetroom}",
                              srcroom=ent, targetroom=thisroom["id"])
            console.msg("{0}: ERROR: Entrance room does not exist: {0}".format(NAME, ent))
            continue

        # Enumerate the exits in the entrance source room.
        exits = []
        for ex in enumerate(srcroom["exits"]):
            if ex[1]["dest"] == thisroom["id"]:
                exits.append(ex)
        entcount += len(exits)

        # Delete the entrances from the source room.
        offset = 0
        for ex in exits:
            del srcroom["exits"][ex[0]-offset]
            offset += 1

        # Update the source room.
        console.database.upsert_room(srcroom)

    # Clear the entrance list in the current room, and report.
    roomcount = len(thisroom["entrances"])
    thisroom["entrances"] = []
    console.database.upsert_room(thisroom)
    console.msg("{0}: Deleted {1} entrances from {2} rooms.".format(NAME, entcount, roomcount))
    return True
