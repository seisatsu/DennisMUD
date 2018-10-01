#####################
# Dennis MUD        #
# redirect_exit.py  #
# Copyright 2018    #
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

NAME = "redirect exit"
CATEGORIES = ["exits"]
USAGE = "redirect exit <id> <destination>"
DESCRIPTION = "Set the destination of the exit <id> in this room to <destination>."


def COMMAND(console, database, args):
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        exitid = int(args[0])
        dest = int(args[1])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure the exit is in this room.
    thisroom = database.room_by_id(console.user["room"])
    if thisroom:
        if exitid > len(thisroom["exits"])-1 or exitid < 0:
            console.msg(NAME + ": no such exit")
            return False
        # Check if the destination room exists.
        destroom = database.room_by_id(dest)
        if not destroom:
            console.msg(NAME + ": destination room does not exist")
            return False  # The destination room does not exist.
        if thisroom["locked"] and not console.user["wizard"] and console.user["name"] not in thisroom["owners"]:
            console.msg(NAME + ": the room is locked")
            return False
        thisroom["exits"][exitid]["dest"] = dest
        database.upsert_room(thisroom)
        console.msg(NAME + ": done")
        return True
    console.msg("warning: current room does not exist")
    return False
