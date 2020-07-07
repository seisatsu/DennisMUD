#####################
# Dennis MUD        #
# give.py           #
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

NAME = "give"
CATEGORIES = ["items", "users"]
USAGE = "give <username> <item>"
DESCRIPTION = """Give the item called <item> to the user <username>.

You may use a full or partial item name and username. Also works by item ID.
The item must be in your inventory, and the recipient must be online and in the same room as you.
Wizards can give any item they are holding to any user anywhere, even an offline one.

Ex. `give seisatsu jar of dirt`
Ex2. `give seisatsu 4`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Lookup the current room.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # Get item name/id.
    target = ' '.join(args[1:]).lower()
    if target == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Make sure the named user exists, is online, and is in the same room as us.
    targetuser = COMMON.check_user(NAME, console, args[0].lower(), room=True, online=True, live=True, reason=False,
                                   wizardskip=["room", "online"])
    if not targetuser:
        # Check for a partial user match, and try running again if there's just one.
        print(args)
        partial = COMMON.match_partial(NAME, console, args[0].lower(), "user")
        if partial:
            argstemp = args[1:]
            argstemp.insert(0, partial[0])
            print(argstemp)
            return COMMAND(console, argstemp)
        console.msg("{0}: No such user in this room.".format(NAME))
        return False

    # Search our inventory for the target item.
    for itemid in console.user["inventory"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid, reason=False)
        if not thisitem:
            console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                              item=itemid)
            console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
            continue

        # If we find the correct item, give it to the named user.
        if target in [thisitem["name"].lower(), "the " + thisitem["name"].lower()] or str(thisitem["id"]) == target:
            # Make sure the named user doesn't already have the item. (It could be duplified.)
            if itemid in targetuser["inventory"]:
                console.msg("{0}: That user already has this item.".format(NAME))
                return False

            # Only non-owners lose duplified items when giving them to someone.
            if not thisitem["duplified"] or not console.user["name"] in thisitem["owners"]:
                console.user["inventory"].remove(thisitem["id"])

            # Add the item to the target user's inventory.
            targetuser["inventory"].append(itemid)

            # Send messages to ourselves and the target user.
            console.msg("You gave {0} {1}.".format(targetuser["nick"], COMMON.format_item(NAME, thisitem["name"])))
            console.shell.msg_user(args[0].lower(),
                                   "{0} gave you {1}.".format(console.user["nick"],
                                                              COMMON.format_item(NAME, thisitem["name"])))

            # Update our user document.
            console.database.upsert_user(console.user)

            # Update the target user's document.
            console.database.upsert_user(targetuser)

            # Finished.
            return True

    # We didn't find the requested item. Check for a partial match.
    partial = COMMON.match_partial(NAME, console, target, "item", room=False, inventory=True)
    if partial:
        argstemp = partial
        argstemp.insert(0, args[0].lower())
        return COMMAND(console, argstemp)

    # Maybe the user accidentally typed "give item <item>".
    if args[0].lower() == "item":
        console.msg("{0}: Maybe you meant \"give {1}\".".format(NAME, ' '.join(args[1:])))

    return False
