#####################
# Dennis MUD        #
# use.py            #
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

NAME = "use"
CATEGORIES = ["items"]
ALIASES = ["u"]
USAGE = "use <item>"
DESCRIPTION = """Use the item called <item> in your inventory or the room. Works by item name or ID.

This will broadcast an action, and might teleport you if the item is a telekey.

Ex. `use 4` to show the custom action for item 4.
Ex2. `use Crystal Ball` to show the custom action for the item named "Crystal Ball"."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Get item name or id.
    target = ' '.join(args).lower()
    if target == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Reference to whatever item we do or don't find in the room.
    itemref = None

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # Search for the item in our inventory.
    for itemid in console.user["inventory"]:
        thisitem = console.database.item_by_id(itemid)
        # A reference was found to a nonexistent item. Report this and continue searching.
        if not thisitem:
            console.log.error("Item referenced in user inventory does not exist: {user} :: {item}",
                              user=console.user["name"], item=itemid)
            console.msg("{0}: ERROR: Item referenced in your inventory does not exist: {1}".format(NAME, itemid))
            continue

        # Check for name or id match.
        if thisitem["name"].lower() == target or str(thisitem["id"]) == target:
            itemref = thisitem
            break

    # We didn't find it in our inventory, so search for the item in the current room.
    if not itemref:
        for itemid in thisroom["items"]:
            thisitem = console.database.item_by_id(itemid)
            # A reference was found to a nonexistent item. Report this and continue searching.
            if not thisitem:
                console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                                  item=itemid)
                console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
                continue

            # Check for name or id match.
            if thisitem["name"].lower() == target or str(thisitem["id"]) == target:
                itemref = thisitem
                break

    # The item was found. See what it does.
    if itemref:
        # This item has a custom action.
        if itemref["action"]:
            # Broadcast a custom item action.
            COMMON.broadcast_action(NAME, console, itemref["action"])

        # This item has no custom action. Format and broadcast the default item action.
        else:
            action = "{0} used {1}.".format(console.user["nick"], COMMON.format_item(NAME, itemref["name"]))
            console.shell.broadcast_room(console, action)

        # The item is a telekey. Prepare for teleportation.
        if itemref["telekey"] is not None:
            # Lookup the destination room and perform room checks.
            destroom = COMMON.check_room(NAME, console, itemref["telekey"])

            # The telekey is paired to a nonexistent room. Report and ignore it.
            if not destroom:
                console.msg(
                    "{0}: ERROR: This telekey is paired to a nonexistent room: {1} -> {2}".format(NAME,
                                                                                                  itemref["id"],
                                                                                                  itemref["telekey"]
                                                                                                  ))
                console.log.error("Telekey is paired to a nonexistent room: {item} -> {room}", item=itemref["id"],
                                  room=itemref["telekey"])

            # Proceed with teleportation.
            else:
                # Remove us from the current room.
                if console.user["name"] in thisroom["users"]:
                    thisroom["users"].remove(console.user["name"])

                # Add us to the destination room.
                if console.user["name"] not in destroom["users"]:
                    destroom["users"].append(console.user["name"])

                # Broadcast our teleportation to the origin room.
                console.shell.broadcast_room(console, "{0} vanished from the room.".format(console.user["nick"]))

                # Set our current room to the new room.
                console.user["room"] = destroom["id"]

                # Broadcast our arrival to the destination room, but not to ourselves.
                console.shell.broadcast_room(console, "{0} entered the room.".format(console.user["nick"]),
                                             exclude=console.user["name"])

                # Save the origin room, the destination room, and our user document.
                console.database.upsert_room(thisroom)
                console.database.upsert_room(destroom)
                console.database.upsert_user(console.user)

                # Take a look around.
                console.shell.command(console, "look", False)

        # Finished.
        return True

    # We didn't find the requested item. Check for a partial match.
    partial = COMMON.match_partial(NAME, console, target, "item", room=True, inventory=True)
    if partial:
        return COMMAND(console, partial)

    # Maybe the user accidentally typed "use item <item>".
    if args[0].lower() == "item":
        console.msg("{0}: Maybe you meant \"use {1}\".".format(NAME, ' '.join(args[1:])))

    return False

