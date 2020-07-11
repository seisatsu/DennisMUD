#####################
# Dennis MUD        #
# return_room.py    #
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

NAME = "return room"
CATEGORIES = ["items", "ownership", "rooms"]
USAGE = "return room"
DESCRIPTION = """Return all of the items in the current room to their primary owners.

You must own the room.
If the primary owner already has an item (for example if it's duplified), you will just lose it.
If you are the primary owner of an item, nothing will happen with it.

Ex. `return room` to return all items in the current room."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console, owner=True)
    if not thisroom:
        return False

    # Cycle through the room, keeping track of how many items we returned and kept.
    # We also need to copy the room's list of items, or the iterator will break.
    retcount = 0
    keepcount = 0
    itemlist = thisroom["items"].copy()
    for itemid in itemlist:
        print("test", itemid)
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid, reason=False)
        if not thisitem:
            console.log.error("Item in room does not exist: {0} :: {1}".format(console.user["room"], itemid))
            console.msg("{0}: ERROR: Item in the current room does not exist: {0}".format(NAME, itemid))
            continue

        # Make sure the item's primary owner exists.
        targetuser = COMMON.check_user(NAME, console, thisitem["owners"][0], live=True, reason=False)
        if not targetuser:
            console.log.error("Primary owner for item does not exist: {0} :: {1}".format(itemid, thisitem["owners"][0]))
            console.msg("{0}: ERROR: Primary owner does not exist for this item: {0}".format(NAME,
                                                                                             thisitem["owners"][0]))
            continue

        # Remove the item from the room
        print("test2", itemid)
        thisroom["items"].remove(itemid)
        console.database.upsert_room(thisroom)

        # If the item isn't already in the primary owner's inventory, put it there.
        # Keep track of whether it was ours or someone else's.
        if itemid not in targetuser["inventory"]:
            targetuser["inventory"].append(itemid)
            console.database.upsert_user(targetuser)
            if targetuser["name"] == console.user["name"]:
                keepcount += 1
            else:
                retcount += 1

        # If they are online, notify the primary owner that they have received the item.
        console.shell.msg_user(thisitem["owners"][0], "{0} appeared in your inventory.".format(
            COMMON.format_item(NAME, thisitem["name"], upper=True)))

    # Finished.
    console.msg("{0}: Total items returned: {1}; items received: {2}".format(NAME, retcount, keepcount))
    return True