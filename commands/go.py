#####################
# Dennis MUD        #
# go.py             #
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

NAME = "go"
CATEGORIES = ["exploration"]
USAGE = "go <exit>"
DESCRIPTION = "Take the exit called <exit> to wherever it may lead."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Look for the current room.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    exits = thisroom["exits"]
    if len(exits):
        for e in exits:
            if e["name"].lower() == ' '.join(args).lower():
                # Check if the destination room exists.
                destroom = database.room_by_id(e["dest"])
                if not destroom:
                    console.msg(NAME + ": destination room does not exist")
                    return False  # The destination room does not exist.

                # Check if the exit is locked.
                if e["locked"] and console.user["name"] not in e["owners"] and not console.user["wizard"]:
                    console.msg(NAME + ": this exit is locked.")
                    return False

                # Move us to the new room.
                if console.user["name"] in thisroom["users"]:
                    thisroom["users"].remove(console.user["name"])
                if console.user["name"] not in destroom["users"]:
                    destroom["users"].append(console.user["name"])
                if e["action"]:
                    console.broadcast_room(console.user["nick"] + " " + e["action"])
                else:
                    console.broadcast_room(console.user["nick"] + " left the room through " + e["name"])
                console.user["room"] = destroom["id"]
                console.broadcast_room(console.user["nick"] + " entered the room")
                database.upsert_room(thisroom)
                database.upsert_room(destroom)
                database.upsert_user(console.user)
                console.command("look", False)
                return True

    console.msg(NAME + ": no such exit")
    return False
