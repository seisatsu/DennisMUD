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
DESCRIPTION = """Give the item called <item> to the user <username>. Also works by item ID.

The item must be in your inventory.

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

    # Make sure the named user exists, is online, and is in the same room as us.
    targetuser = COMMON.check_user(NAME, console, args[0].lower(), room=True, online=True, live=True)
    if not targetuser:
        return False

    # Get item name/id.
    name = ' '.join(args[1:])

    # Search our inventory for the target item.
    for itemid in console.user["inventory"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid)
        if not thisitem:
            return False

        # If we find the correct item, give it to the named user.
        if thisitem["name"].lower() == name.lower() or str(thisitem["id"]) == name:
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

    # The item wasn't found in our inventory.
    console.msg("{0}: No such item in your inventory: {1}".format(NAME, ' '.join(args[1:])))

    # Maybe the user accidentally typed "give item <username> <item>".
    if args[0].lower() == "item":
        console.msg("{0}: Maybe you meant \"give {1}\".".format(NAME, ' '.join(args[1:])))
    return False
