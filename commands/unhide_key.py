#####################
# Dennis MUD        #
# unhide_key.py     #
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

NAME = "unhide key"
CATEGORIES = ["exits"]
USAGE = "unhide key <exit>"
DESCRIPTION = """Allow looking at the locked <exit> to reveal its key.

If the key for an exit is not hidden, looking at the exit will tell the player the name of the item which unlocks it.
You must own the exit or its room to unhide the key.

Ex. `unhide key 3`"""


def COMMAND(console, args):
    if len(args) < 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Make sure the id is an integer.
    try:
        exitid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure the exit is in this room.
    thisroom = console.database.room_by_id(console.user["room"])
    if thisroom:
        if exitid > len(thisroom["exits"])-1 or exitid < 0:
            console.msg(NAME + ": no such exit")
            return False
        if console.user["name"] not in thisroom["exits"][exitid]["owners"] \
                and console.user["name"] not in thisroom["owners"] and not console.user["wizard"]:
            console.msg(NAME + ": you do not own this exit or this room")
            return False
        if not thisroom["exits"][exitid]["key"]:
            console.msg(NAME + ": there is no key paired to this exit")
            return False
        if not thisroom["exits"][exitid]["key_hidden"]:
            console.msg(NAME + ": the key for this exit is already not hidden")
            return False
        thisroom["exits"][exitid]["key_hidden"] = False
        console.database.upsert_room(thisroom)
        console.msg(NAME + ": done")
        return True
    console.msg("warning: current room does not exist")
    return False
