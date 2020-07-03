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

    # No arguments, so just list the room's exits.
    if len(args) == 0:
        exitlist = []

        # Append each exit name and ID to the list.
        for ex in range(len(thisroom["exits"])):
            exitlist.append("{0} ({1})".format(thisroom["exits"][ex]["name"], ex))

        # If any exits were found, show the list.
        if exitlist:
            console.msg("Exits: {0}".format(", ".join(exitlist)))

        # There were no exits.
        else:
            console.msg("{0}: no exits in this room".format(NAME))

        # Finished.
        return True

    # Get exit name/id.
    name = ' '.join(args)

    # Iterate through all of the exits in the room, searching for the one that was asked for.
    exits = thisroom["exits"]
    for ex in range(len(exits)):
        # Check for name or id match.
        if exits[ex]["name"].lower() == name.lower() or str(ex) == name:
            # Check if the destination room exists, otherwise give an error and fail.
            destroom = COMMON.check_room(NAME, console, roomid=exits[ex]["dest"], reason=False)
            if not destroom:
                console.log.error("destination room does not exist for exit: {thisroom} :: {exit} -> {destroom}",
                                  thisoorm=console.user["room"], exit=ex, destroom=exits[ex]["dest"])
                console.msg("{0}: error: destination room does not exist".format(NAME))
                return False

            # Check if the exit is locked.
            if exits[ex]["locked"] and console.user["name"] not in exits[ex]["owners"] \
                    and not console.user["wizard"]:

                # The exit is locked and the player does not have the key.
                if not exits[ex]["key"] in console.user["inventory"]:
                    console.msg("{0}: this exit is locked.".format(NAME))

                    # This lock has a custom action.
                    if exits[ex]["action"]["locked"]:
                        # Format a custom lock action containing a player tag.
                        if "%player%" in exits[ex]["action"]["locked"]:
                            action = exits[ex]["action"]["locked"].replace("%player%", console.user["nick"])

                        # Format a regular custom action.
                        else:
                            action = "{0} {1}".format(console.user["nick"], exits[ex]["action"]["locked"])
                        console.shell.broadcast_room(console, action)

                    # We couldn't take the exit, so fail.
                    return False

                # The exit is locked and the player has the key.
                else:
                    # Check if the key item exists, otherwise give an error and fail.
                    thisitem = COMMON.check_item(NAME, console, exits[ex]["key"], reason=False)
                    if not thisitem:
                        console.log.error("key item in user inventory does not exist: {thisitem}",
                                          thisitem=exits[ex]["key"])
                        console.msg("{0}: error: key item in inventory does not exist".format(NAME))
                        return False

                    # This key item has a custom action.
                    if thisitem["action"]:
                        # Format a custom key action containing a player tag.
                        if "%player%" in thisitem["action"]:
                            action = thisitem["action"].replace("%player%", console.user["nick"])

                        # Format a regular custom key action.
                        else:
                            action = "{0} {1}".format(console.user["nick"], thisitem["action"])

                        # Broadcast the custom key action.
                        console.shell.broadcast_room(console, action)

                    # Format and broadcast the default key action.
                    else:
                        action = "{0} used {1}".format(console.user["nick"], thisitem["name"])
                        console.shell.broadcast_room(console, action)

            # Remove us from the current room.
            if console.user["name"] in thisroom["users"]:
                thisroom["users"].remove(console.user["name"])

            # Add us to the destination room.
            if console.user["name"] not in destroom["users"]:
                destroom["users"].append(console.user["name"])

            # This exit has a custom action.
            if exits[ex]["action"]["go"]:
                # Format a custom exit action containing a player tag.
                if "%player%" in exits[ex]["action"]["go"]:
                    action = exits[ex]["action"]["go"].replace("%player%", console.user["nick"])

                # Format a regular custom action.
                else:
                    action = "{0} {1}".format(console.user["nick"], exits[ex]["action"]["go"])

                # Broadcast the custom exit action.
                console.shell.broadcast_room(console, action)

            # Format and broadcast the default exit action.
            else:
                console.shell.broadcast_room(console, "{0} left the room through {1}".format(
                    console.user["nick"], exits[ex]["name"]))

            # Finish entering the new room and announce our presence.
            console.user["room"] = destroom["id"]
            console.shell.broadcast_room(console, "{0} entered the room".format(console.user["nick"]))

            # Save this room, the destination room, and the current user.
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
