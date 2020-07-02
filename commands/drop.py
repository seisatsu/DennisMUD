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
DESCRIPTION = """Drop the item called <item> into the current room. Also works by item ID.

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
    name = ' '.join(args)

    # Search our inventory for the target item.
    for itemid in console.user["inventory"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid)
        if not thisitem:
            return False

        # If we find the correct item, announce the drop and figure out how to drop it.
        if thisitem["name"].lower() == name.lower() or str(thisitem["id"]) == name:
            # Only non-owners lose duplified items when dropping them.
            if not thisitem["duplified"] or not console.user["name"] in thisitem["owners"]:
                console.user["inventory"].remove(thisitem["id"])

            # If this is a duplified item we do not own, announce that it is going away.
            if thisitem["duplified"] and not console.user["name"] in thisitem["owners"]:
                console.msg("{0} vanished".format(thisitem["name"]))

            # Only put unduplified items into the room unless we are the owner.
            if not thisitem["duplified"] or console.user["name"] in thisitem["owners"]:
                # If the item is not in the room yet, add it.
                if thisitem["id"] in thisroom["items"]:
                    console.msg("{0}: item is already in this room".format(NAME))
                else:
                    thisroom["items"].append(thisitem["id"])
                    console.shell.broadcast_room(console, console.user["nick"] + " dropped " + thisitem["name"])

                # Update the room document.
                console.database.upsert_room(thisroom)

            # Update the user document.
            console.database.upsert_user(console.user)

            # Finished.
            return True

    # The item wasn't found in our inventory.
    console.msg("{0}: no such item in inventory: {1}".format(NAME, ' '.join(args)))

    # Maybe the user accidentally typed "drop item <item>".
    if args[0].lower() == "item":
        console.msg("{0}: maybe you meant \"drop {1}\"".format(NAME, ' '.join(args[1:])))
    return False
