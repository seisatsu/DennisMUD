#######################
# Dennis MUD          #
# return_inventory.py #
# Copyright 2020      #
# Michael D. Reiley   #
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

NAME = "return inventory"
CATEGORIES = ["items", "ownership"]
USAGE = "return inventory"
DESCRIPTION = """Return all of the items in your inventory to their primary owners.

If the primary owner already has an item (for example if it's duplified), you will just lose it.
If you are the primary owner of an item, nothing will happen with it.

Ex. `return inventory` to return all items in your inventory."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Cycle through our inventory, keeping track of how many items we returned and kept.
    retcount = 0
    keepcount = 0
    for itemid in console.user["inventory"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid, reason=False)
        if not thisitem:
            console.log.error("Item in user inventory does not exist: {0} :: {1}".format(console.user["name"], itemid))
            console.msg("{0}: ERROR: Item in your inventory does not exist: {0}".format(NAME, itemid))
            continue

        # Make sure the item's primary owner exists.
        targetuser = COMMON.check_user(NAME, console, thisitem["owners"][0], live=True, reason=False)
        if not targetuser:
            console.log.error("Primary owner for item does not exist: {0} :: {1}".format(itemid, thisitem["owners"][0]))
            console.msg("{0}: ERROR: Primary owner does not exist for this item: {0}".format(NAME,
                                                                                             thisitem["owners"][0]))
            continue

        # Make sure we are not the primary owner. Otherwise, remove the item from our inventory.
        if thisitem["owners"][0] == console.user["name"]:
            keepcount += 1
            continue

        # Remove the item from our inventory.
        console.user["inventory"].remove(itemid)
        retcount += 1

        # If the item isn't already in the primary owner's inventory, put it there.
        if itemid not in targetuser["inventory"]:
            targetuser["inventory"].append(itemid)
            console.database.upsert_user(targetuser)

        # If they are online, notify the primary owner that they have received the item.
        console.shell.msg_user(thisitem["owners"][0], "{0} appeared in your inventory.".format(
            COMMON.format_item(NAME, thisitem["name"], upper=True)))

    # Finished.
    console.msg("{0}: Total items returned: {1}; items kept: {2}".format(NAME, retcount, keepcount))
    console.database.upsert_user(console.user)
    return True
