#####################
# Dennis MUD        #
# break_exit.py     #
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

NAME = "break exit"
CATEGORIES = ["exits"]
ALIASES = ["delete exit", "destroy exit", "remove exit"]
USAGE = "break exit <exit>"
DESCRIPTION = """Break the exit with ID <exit> in the current room.

You must own the exit or its room in order to break it.

Ex. `break exit 3` to break the exit with ID 3 in the current room."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    exitid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if exitid is None:
        return False

    # Lookup the current room, and check if the exit exists in this room.
    thisroom = COMMON.check_exit(NAME, console, exitid, owner=True)
    if not thisroom:
        return False

    # Make sure the current room is not outbound sealed, or we are a room owner or a wizard.
    if thisroom["sealed"]["outbound"] and not console.user["wizard"] and \
            console.user["name"] not in thisroom["owners"]:
        console.msg("{0}: This room is outbound sealed.".format(NAME))
        return False

    # Make sure the exit's destination room exists. Otherwise give an error but delete the exit anyway.
    destroom = COMMON.check_room(NAME, console, thisroom["exits"][exitid]["dest"])
    if not destroom:
        console.log.error("Exit destination room does not exist: {roomid}", roomid=destroom["id"])
        console.msg("ERROR: Exit destination room does not exist: {0}".format(destroom["id"]))

        # Delete the exit.
        del thisroom["exits"][exitid]
        console.database.upsert_room(thisroom)

        # Finished successfully but with an error.
        console.msg("{0}: Done.".format(NAME))
        return True

    # Delete the exit. If this was the only exit leading to the destination room,
    # remove this room from the destination room's entrances record.
    del thisroom["exits"][exitid]
    only_exit_to_destroom = True
    for ex in thisroom["exits"]:
        if ex["dest"] == destroom["id"]:
            only_exit_to_destroom = False
            break
    if only_exit_to_destroom:
        destroom["entrances"].remove(thisroom["id"])
        console.database.upsert_room(destroom)
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True

