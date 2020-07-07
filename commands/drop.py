#####################
# Dennis MUD        #
# drop.py           #
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

NAME = "drop"
CATEGORIES = ["items"]
USAGE = "drop <item>"
DESCRIPTION = """Drop the item called <item> into the current room. Works by name or ID.

Duplified items will vanish when you drop them, unless you own them.

Ex. `drop crystal ball`
Ex2. `drop 4`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Lookup the current room.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # Get item name/id.
    target = ' '.join(args).lower()
    if target == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Record partial matches.
    partials = []

    # Search our inventory for the target item.
    for itemid in console.user["inventory"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid, reason=False)
        if not thisitem:
            console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                              item=itemid)
            console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
            continue

        # Check for partial matches.
        if target in thisitem["name"].lower() or target.replace("the ", "", 1) in thisitem["name"].lower():
            partials.append(thisitem["name"].lower())

        # Check for name or id match. Also check if the user prepended "the ". Figure out how to drop it.
        if target in [thisitem["name"].lower(), "the " + thisitem["name"].lower()] or str(thisitem["id"]) == target:
            # Only non-owners lose duplified items when dropping them.
            if not thisitem["duplified"] or not console.user["name"] in thisitem["owners"]:
                console.user["inventory"].remove(thisitem["id"])

            # If this is a duplified item we do not own, announce that it is going away.
            if thisitem["duplified"] and not console.user["name"] in thisitem["owners"]:
                console.msg("{0} vanished.".format(thisitem["name"]))

            # Only put unduplified items into the room unless we are the owner.
            if not thisitem["duplified"] or console.user["name"] in thisitem["owners"]:
                # If the item is not in the room yet, add it.
                if thisitem["id"] in thisroom["items"]:
                    console.msg("{0}: This item is already in this room.".format(NAME))
                else:
                    thisroom["items"].append(thisitem["id"])
                    console.shell.broadcast_room(console, "{0} dropped {1}.".format(
                        console.user["nick"], COMMON.format_item(NAME, thisitem["name"])))

                # Update the room document.
                console.database.upsert_room(thisroom)

            # Update the user document.
            console.database.upsert_user(console.user)

            # Finished.
            return True

    # We didn't find the requested item.
    # We got exactly one partial match. Assume that one.
    if len(target) >= 3 and len(partials) == 1:
        return COMMAND(console, partials[0].split(' '))

    # We got up to 5 partial matches. List them.
    elif partials and len(partials) <= 5:
        console.msg("{0}: Did you mean one of: {1}".format(NAME, ', '.join(partials)))
        return False

    # We got too many matches.
    elif len(partials) > 5:
        console.msg("{0}: Too many possible matches.".format(NAME))
        return False

    # Maybe the user accidentally typed "drop item <item>".
    if args[0].lower() == "item":
        console.msg("{0}: Maybe you meant \"drop {1}\".".format(NAME, ' '.join(args[1:])))

    # Really nothing.
    else:
        console.msg("{0}: No such item in your inventory: {1}".format(NAME, ' '.join(args)))

    return False
