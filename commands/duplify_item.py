#####################
# Dennis MUD        #
# duplify_item.py   #
# Copyright 2019    #
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

NAME = "duplify item"
CATEGORIES = ["items"]
USAGE = "duplify item <item>"
DESCRIPTION = """Duplify the item with ID <item>, so that any number of people can pick it up.

When a user besides the owner `get`s a duplified item, it doesn't disappear from the room it is in.
Any number of users may be holding the duplified item.
When the owner uses `break item` on a duplified item, all copies will break.
When a user besides the owner drops a duplified item, it will vanish.
Duplified items exist permanently in the owner's inventory until broken, and can be dropped in multiple places.
This feature is particularly useful for keys.
You can undo this with the `unduplify item` command.
You must own the item and it must be in your inventory in order to duplify it.

Ex. `duplify item 4`"""


def COMMAND(console, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        itemid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Check if the item exists.
    i = console.database.item_by_id(itemid)
    if i:
        # Make sure we are the item's owner.
        if console.user["name"] not in i["owners"] and not console.user["wizard"]:
            console.msg(NAME + ": you do not own this item")
            return False
        # Make sure we are holding the item.
        if itemid in console.user["inventory"] or console.user["wizard"]:
            # Duplify the item.
            if i["duplified"]:
                console.msg(NAME + ": item is already duplified")
                return False
            i["duplified"] = True
            console.database.upsert_item(i)
            console.msg(NAME + ": done")
            return True
        else:
            # We are not holding that item.
            console.msg(NAME + ": not holding item")
            return False

    else:
        # No item with that ID exists.
        console.msg(NAME + ": no such item")
        return False
