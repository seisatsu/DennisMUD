#####################
# Dennis MUD        #
# return_item.py    #
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

NAME = "return item"
CATEGORIES = ["items", "ownership"]
USAGE = "return item <item_id>"
DESCRIPTION = """Return the item <item_id> to the inventory of its primary owner.

You must be holding the item in order to return it.
If the primary owner already has the item (for example if it's duplified), you will just lose it.
If you are the primary owner of the item, nothing will happen with it.

Ex. `return item 4` to return item 4."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, holding=True, orwizard=False)
    if not thisitem:
        return False

    # Make sure the item's primary owner exists.
    targetuser = COMMON.check_user(NAME, console, thisitem["owners"][0], live=True, reason=False)
    if not targetuser:
        console.log.error("Primary owner for item does not exist: {0} :: {1}".format(itemid, thisitem["owners"][0]))
        console.msg("{0}: ERROR: Primary owner does not exist for this item: {0}".format(NAME, thisitem["owners"][0]))
        return False

    # Make sure we are not the primary owner.
    if thisitem["owners"][0] == console.user["name"]:
        console.msg("{0}: You are the primary owner of this item.".format(NAME))
        return False

    # Remove the item from our inventory.
    if itemid in console.user["inventory"]:
        console.user["inventory"].remove(thisitem["id"])
        console.database.upsert_user(console.user)

    # If the item isn't already in the primary owner's inventory, put it there.
    if itemid not in targetuser["inventory"]:
        targetuser["inventory"].append(itemid)
        console.database.upsert_user(targetuser)

    # Tell us that we returned the item successfully.
    console.msg("{0}: Returned {1} from our inventory to its primary owner.".format(
        NAME, COMMON.format_item(NAME, thisitem["name"])))

    # If they are online, notify the primary owner that they have received the item.
    console.shell.msg_user(thisitem["owners"][0], "{0} appeared in your inventory.".format(
        COMMON.format_item(NAME, thisitem["name"], upper=True)))

    # Finished.
    return True
