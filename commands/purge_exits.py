#####################
# Dennis MUD        #
# purge_exits.py    #
# Copyright 2021    #
# Sei Satzparad     #
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

NAME = "purge exits"
CATEGORIES = ["exits"]
USAGE = "purge exits"
DESCRIPTION = """Break all exits in the current room.

You must own the room in order to purge its exits.
Wizards can purge the exits from any room.

Ex. `purge exits` to break every exit in the current room."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console, owner=True)
    if not thisroom:
        return False

    # Make sure this room has any exits.
    if not thisroom["exits"]:
        console.msg("{0}: This room has no exits.".format(NAME))
        return False

    # Delete each exit in the room, handling destination entrances if necessary.
    # We delete the exits from a copy of the exit list and then merge it in at the end.
    # This prevents the exit IDs from changing while we are processing the list.
    newexitlist = thisroom["exits"].copy()
    for exitid in range(len(thisroom["exits"])):
        # Make sure the exit's destination room exists. Otherwise give an error but delete the exit anyway.
        destroom = COMMON.check_room(NAME, console, thisroom["exits"][exitid]["dest"])
        if not destroom:
            console.log.error("Exit destination room does not exist: {roomid}", roomid=destroom["id"])
            console.msg("ERROR: Exit destination room does not exist: {0}".format(destroom["id"]))

            # Delete the exit, then continue. Since the exit ID is the list index, we are deleting the first
            # exit in newexitlist each time instead of deleting by index.
            del newexitlist[0]
            continue

        else:
            # Delete the exit. Remove this room from the destination room's entrances record if it is there,
            # since all of the exits leading from here to there will eventually be gone.
            del newexitlist[0]
            if thisroom["id"] in destroom["entrances"]:
                destroom["entrances"].remove(thisroom["id"])
                console.database.upsert_room(destroom)

    # Update the exit list in the current room, and report.
    excount = len(thisroom["exits"])
    thisroom["exits"] = newexitlist
    console.database.upsert_room(thisroom)
    console.msg("{0}: Deleted {1} exits.".format(NAME, excount))
    return True

