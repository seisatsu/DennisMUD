#######################
# Dennis MUD          #
# go.py               #
# Copyright 2018-2021 #
# Sei Satzparad       #
#######################

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
ALIASES = ["exit", "exit through", "go into", "go through", "leave", "leave through"]
SPECIAL_ALIASES = ['>']
USAGE = "go [exit]"
DESCRIPTION = """Take the exit called <exit> to wherever it may lead.

You may use a full or partial exit name, or the exit ID.
If no argument is given, list the exits in the current room instead.
If the exit is locked, you will not be able to enter without a key.
Wizards can enter any locked exit.

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
            console.msg("{0}: No exits in this room. Make one or use `xyzzy` to return to the first room.".format(NAME))

        # Finished.
        return True

    # Get exit name/id.
    target = ' '.join(args).lower()
    if target == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Iterate through all of the exits in the room, searching for the one that was asked for.
    exits = thisroom["exits"]
    for ex in range(len(exits)):

        # Check for name or id match.
        if exits[ex]["name"].lower() == target.lower() or str(ex) == target:
            # Check if the destination room exists, otherwise give an error and fail.
            destroom = COMMON.check_room(NAME, console, roomid=exits[ex]["dest"], reason=False)
            if not destroom:
                console.log.error("Destination room does not exist for exit: {thisroom} :: {exit} -> {destroom}",
                                  thisoorm=console.user["room"], exit=ex, destroom=exits[ex]["dest"])
                console.msg("{0}: ERROR: Destination room does not exist.".format(NAME))
                return False

            # Check if the exit is locked.
            if exits[ex]["locked"] and console.user["name"] not in exits[ex]["owners"] \
                    and not console.user["wizard"]:

                # The exit is locked and the player does not have the key.
                if not exits[ex]["key"] in console.user["inventory"]:
                    console.msg("{0}: This exit is locked.".format(NAME))

                    # This lock has a custom action.
                    if exits[ex]["action"]["locked"]:
                        # Broadcast a custom lock action if one exists.
                        if "%player%" in exits[ex]["action"]["locked"]:
                            COMMON.broadcast_action(NAME, console, exits[ex]["action"]["locked"])

                    # We couldn't take the exit, so fail.
                    return False

                # The exit is locked and the player has the key.
                else:
                    # Check if the key item exists, otherwise give an error and fail.
                    thisitem = COMMON.check_item(NAME, console, exits[ex]["key"], reason=False)
                    if not thisitem:
                        console.log.error("Key item referenced in user inventory does not actually exist: {thisitem}",
                                          thisitem=exits[ex]["key"])
                        console.msg(
                            "{0}: ERROR: Key item referenced in your inventory does not actually exist.".format(NAME))
                        return False

                    # This key item has a custom action.
                    if thisitem["action"]:
                        # Broadcast a custom key action.
                        COMMON.broadcast_action(NAME, console, thisitem["action"])

                    # Format and broadcast the default key action.
                    else:
                        action = "{0} used {1}".format(console.user["nick"], thisitem["name"])
                        console.shell.broadcast_room(console, action)

            # Stand up if we aren't already.
            if console["posture"]:
                COMMON.posture(NAME, console)

            # Remove us from the current room.
            if console.user["name"] in thisroom["users"]:
                thisroom["users"].remove(console.user["name"])

            # Add us to the destination room.
            if console.user["name"] not in destroom["users"]:
                destroom["users"].append(console.user["name"])

            # This exit has a custom action.
            if exits[ex]["action"]["go"]:
                # Broadcast a custom exit action.
                COMMON.broadcast_action(NAME, console, exits[ex]["action"]["go"])

            # Format and broadcast the default exit action.
            else:
                console.shell.broadcast_room(console, "{0} left the room through {1}.".format(
                    console.user["nick"], exits[ex]["name"]))

            # Set our current room to the new room.
            console.user["room"] = destroom["id"]

            # This entrance has a custom action.
            if exits[ex]["action"]["entrance"]:
                # Broadcast a custom entrance action.
                COMMON.broadcast_action(NAME, console, exits[ex]["action"]["entrance"])

            # Format and broadcast the default entrance action, except to ourselves.
            else:
                console.shell.broadcast_room(console, "{0} entered the room.".format(console.user["nick"]),
                                             exclude=console.user["name"])

            # Save this room, the destination room, and the current user.
            console.database.upsert_room(thisroom)
            console.database.upsert_room(destroom)
            console.database.upsert_user(console.user)

            # If autolook is enabled, look.
            if console.user["autolook"]["enabled"]:
                console.shell.command(console, "look", False)
            else:
                console.msg("{0} ({1})".format(thisroom["name"], thisroom["id"]))

            # Update console's exit list.
            console.exits = []
            for exi in range(len(destroom["exits"])):
                console.exits.append(destroom["exits"][exi]["name"])

            # Finished.
            return True

    # We didn't find the requested exit. Check for a partial match.
    partial = COMMON.match_partial(NAME, console, target, "exit")
    if partial:
        return COMMAND(console, partial)

    return False
