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


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Test input.
    try:
        exitid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Find the current room, and make sure it exists.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False

    # Find out if the exit exists in this room.
    if exitid > len(thisroom["exits"])-1 or exitid < 0:
        console.msg(NAME + ": no such exit")
        return False
    if thisroom["sealed"]["outbound"] and not console.user["wizard"] and \
            console.user["name"] not in thisroom["owners"]:
        console.msg(NAME + ": this room is outbound sealed")
        return False
    if console.user["name"] not in thisroom["exits"][exitid]["owners"] \
            and console.user["name"] not in thisroom["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this exit or this room")
        return False

    # Delete the exit. If this was the only exit leading to the destination room,
    # remove this room from the destination room's entrances record.
    destroom = database.room_by_id(thisroom["exits"][exitid]["dest"])
    del thisroom["exits"][exitid]
    only_exit_to_destroom = True
    for ex in thisroom["exits"]:
        if ex["dest"] == destroom["id"]:
            only_exit_to_destroom = False
            break
    if only_exit_to_destroom:
        destroom["entrances"].remove(thisroom["id"])
        database.upsert_room(destroom)
    database.upsert_room(thisroom)

    console.msg(NAME + ": done")
    return True

