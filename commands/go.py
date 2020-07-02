#####################
# Dennis MUD        #
# go.py             #
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

NAME = "go"
CATEGORIES = ["exploration"]
ALIASES = ["exit"]
SPECIAL_ALIASES = ['>']
USAGE = "go [exit]"
DESCRIPTION = """Take the exit called <exit> to wherever it may lead. Also works by exit ID.

If no argument is given, list the exits in the current room instead.

Ex. `go blue door`
Ex2. `go 2`
Ex3. `exit blue door`
Ex4. `>blue door`
Ex5. `go` to list exits."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args):
        return False

    # Lookup the current room.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    if len(args) == 0:
        # Just list exits.
        exitlist = []
        for ex in range(len(thisroom["exits"])):
            exitlist.append("{0} ({1})".format(thisroom["exits"][ex]["name"], ex))
        if exitlist:
            console.msg("Exits: {0}".format(", ".join(exitlist)))
        else:
            console.msg("{0}: no exits in this room".format(NAME))
        return True

    # Get exit name/id.
    name = ' '.join(args)

    # Try to find the exit.
    exits = thisroom["exits"]
    if len(exits):
        for ex in range(len(exits)):
            # Check for name or id match.
            if exits[ex]["name"].lower() == name.lower() or str(ex) == name:
                # Check if the destination room exists.
                destroom = COMMON.check_room(NAME, console, roomid=exits[ex]["dest"], reason=False)
                if not destroom:
                    console.log.error("destination room does not exist for exit: {thisroom} :: {exit} -> {destroom}",
                                      thisoorm=console.user["room"], exit=ex, destroom=exits[ex]["dest"])
                    console.msg("{0}: error: destination room does not exist".format(NAME))
                    return False

                # Check if the exit is locked.
                if exits[ex]["locked"] and console.user["name"] not in exits[ex]["owners"] \
                        and not console.user["wizard"]:
                    # Check whether the user has the key, if any. Broadcast the lock action.
                    if not exits[ex]["key"] in console.user["inventory"]:
                        console.msg("{0}: this exit is locked.".format(NAME))
                        if exits[ex]["action"]["locked"]:
                            if "%player%" in exits[ex]["action"]["locked"]:
                                action = exits[ex]["action"]["locked"].replace("%player%", console.user["nick"])
                            else:
                                action = "{0} {1}".format(console.user["nick"], exits[ex]["action"]["locked"])
                            console.shell.broadcast_room(console, action)
                        return False

                    # The player has the key. Broadcast the action for the key item.
                    else:
                        # Lookup the key item and perform item checks.
                        thisitem = COMMON.check_item(NAME, console, exits[ex]["key"], reason=False)
                        if not thisitem:
                            console.log.error("key item in user inventory does not exist: {thisitem}",
                                              thisitem=exits[ex]["key"])
                            console.msg("{0}: error: key item in inventory does not exist".format(NAME))
                            return False
                        if thisitem["action"]:
                            if "%player%" in thisitem["action"]:
                                action = thisitem["action"].replace("%player%", console.user["nick"])
                            else:
                                action = "{0} {1}".format(console.user["nick"], thisitem["action"])
                            console.shell.broadcast_room(console, action)
                        else:
                            action = "{0} used {1}".format(console.user["nick"], thisitem["name"])
                            console.shell.broadcast_room(console, action)

                # Move us to the new room. Broadcast the exit action if one exists.
                if console.user["name"] in thisroom["users"]:
                    thisroom["users"].remove(console.user["name"])
                if console.user["name"] not in destroom["users"]:
                    destroom["users"].append(console.user["name"])
                if exits[ex]["action"]["go"]:
                    if "%player%" in exits[ex]["action"]["go"]:
                        action = exits[ex]["action"]["go"].replace("%player%", console.user["nick"])
                    else:
                        action = "{0} {1}".format(console.user["nick"], exits[ex]["action"]["go"])
                    console.shell.broadcast_room(console, action)
                else:
                    console.shell.broadcast_room(console, "{0} left the room through {1}".format(
                        console.user["nick"], exits[ex]["name"]))

                # Finish entering the new room and announce our presence.
                console.user["room"] = destroom["id"]
                console.shell.broadcast_room(console, "{0} entered the room".format(console.user["nick"]))

                # Update everything.
                console.database.upsert_room(thisroom)
                console.database.upsert_room(destroom)
                console.database.upsert_user(console.user)

                # If autolook is enabled, look.
                if console.user["autolook"]["enabled"]:
                    console.shell.command(console, "look", False)
                else:
                    console.msg("{0} ({1})".format(thisroom["name"], thisroom["id"]))

                # Finished.
                return True

    # We didn't find the requested exit.
    console.msg("{0}: no such exit: {1}".format(NAME, ' '.join(args)))
    return False
