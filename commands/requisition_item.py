#####################
# Dennis MUD        #
# requisition.py    #
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

NAME = "requisition item"
CATEGORIES = ["items"]
USAGE = "requisition item <id>"
DESCRIPTION = """Obtain the item with id <item>, regardless of where it is.

Whether the item is in another room or someone else's inventory, it will be moved to your inventory.
You can only requisition an item that you own.
Duplified items will just copy to your inventory if not there already.

Ex. `requisition item 14` to move item 14 to your inventory."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=False)
    if not thisitem:
        return False

    # Do nothing if we are already holding the item.
    if itemid in console.user["inventory"]:
        console.msg("{0}: This item is already in your inventory.")
        return False

    # Announce the requisitioning.
    console.msg("Requisitioned item: {0} ({1})".format(thisitem["name"], thisitem["id"]))

    # Don't remove duplified items.
    if not thisitem["duplified"]:
        # If the item is in a room's item list, remove it and announce its disappearance.
        for room in console.database.rooms.all():
            if itemid in room["items"]:
                room["items"].remove(itemid)
                console.router.broadcast_room(room["id"], "{0} vanished from the room.".format(
                    COMMON.format_item(NAME, thisitem["name"], upper=True)))
                console.database.upsert_room(room)

        # If the item is in someone's inventory, remove it and announce its disappearance.
        for user in console.router.users.values():
            if itemid in user["console"].user["inventory"]:
                user["console"].user["inventory"].remove(itemid)
                user["console"].msg("{0} vanished from your inventory.".format(
                    COMMON.format_item(NAME, thisitem["name"], upper=True)))
                console.database.upsert_user(user["console"].user)

    # Place the item in our inventory and announce its appearance.
    console.user["inventory"].append(itemid)
    console.database.upsert_user(console.user)
    console.msg("{0} appeared in your inventory.".format(COMMON.format_item(NAME, thisitem["name"], upper=True)))
    return True
