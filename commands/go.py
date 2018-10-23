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
USAGE = "go [exit]"
DESCRIPTION = """Take the exit called <exit> to wherever it may lead. Also works by exit ID. Aliases: exit and >

If no argument is given, list the exits in the current room instead.

Ex. `go blue door`
Ex2. `go 2`
Ex3. `exit blue door`
Ex4. `>blue door`
Ex5. `go` to list exits."""


def COMMAND(console, database, args):
    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Look for the current room.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    if len(args) == 0:
        # Just list exits.
        exitlist = []
        for e in range(len(thisroom["exits"])):
            exitlist.append(thisroom["exits"][e]["name"] + " (" + str(e) + ")")
        if exitlist:
            console.msg("Exits: " + ", ".join(exitlist))
        else:
            console.msg(NAME + ": no exits in this room")
        return True

    # Get exit name/id.
    name = ' '.join(args)

    # Try to find the exit.
    exits = thisroom["exits"]
    if len(exits):
        for e in range(len(exits)):
            # Check for name or id match.
            if exits[e]["name"].lower() == name.lower() or str(e) == name:
                # Check if the destination room exists.
                destroom = database.room_by_id(exits[e]["dest"])
                if not destroom:
                    console.msg(NAME + ": destination room does not exist")
                    return False  # The destination room does not exist.

                # Check if the exit is locked.
                if exits[e]["locked"] and console.user["name"] not in exits[e]["owners"] and not console.user["wizard"]:
                    # Check whether the user has the key, if any.
                    if not exits[e]["key"] in console.user["inventory"]:
                        console.msg(NAME + ": this exit is locked.")
                        if exits[e]["action"]["locked"]:
                            if "%player%" in exits[e]["action"]["locked"]:
                                action = exits[e]["action"]["locked"].replace("%player%", console.user["nick"])
                            else:
                                action = console.user["nick"] + " " + exits[e]["action"]["locked"]
                            console.broadcast_room(action)
                        return False
                    else:
                        # Broadcast the action for the key item.
                        i = database.item_by_id(exits[e]["key"])
                        if i["action"]:
                            if "%player%" in i["action"]:
                                action = i["action"].replace("%player%", console.user["nick"])
                            else:
                                action = console.user["nick"] + " " + i["action"]
                            console.broadcast_room(action)
                        else:
                            action = console.user["nick"] + " used " + i["name"]
                            console.broadcast_room(action)

                # Move us to the new room.
                if console.user["name"] in thisroom["users"]:
                    thisroom["users"].remove(console.user["name"])
                if console.user["name"] not in destroom["users"]:
                    destroom["users"].append(console.user["name"])
                if exits[e]["action"]["go"]:
                    if "%player%" in exits[e]["action"]["go"]:
                        action = exits[e]["action"]["go"].replace("%player%", console.user["nick"])
                    else:
                        action = console.user["nick"] + " " + exits[e]["action"]["go"]
                    console.broadcast_room(action)
                else:
                    console.broadcast_room(console.user["nick"] + " left the room through " + exits[e]["name"])
                console.user["room"] = destroom["id"]
                console.broadcast_room(console.user["nick"] + " entered the room")
                database.upsert_room(thisroom)
                database.upsert_room(destroom)
                database.upsert_user(console.user)
                console.command("look", False)
                return True

    console.msg(NAME + ": no such exit")
    return False
