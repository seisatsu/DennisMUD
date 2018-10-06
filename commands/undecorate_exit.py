######################
# Dennis MUD         #
# undecorate_exit.py #
# Copyright 2018     #
# Michael D. Reiley  #
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

NAME = "undecorate exit"
CATEGORIES = ["exits"]
USAGE = "undecorate exit <id>"
DESCRIPTION = "Remove the custom action displayed after the player's name when they use the exit <id>."


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        exitid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure the exit is in this room.
    thisroom = database.room_by_id(console.user["room"])
    if thisroom:
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
        if not thisroom["exits"][exitid]["action"]:
            console.msg(NAME + ": the exit already has no custom action")
            return False
        thisroom["exits"][exitid]["action"] = ""
        database.upsert_room(thisroom)
        console.msg(NAME + ": done")
        return True
    console.msg("warning: current room does not exist")
    return False
