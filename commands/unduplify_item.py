#####################
# Dennis MUD        #
# unduplify_item.py #
# Copyright 2018    #
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

NAME = "unduplify item"
CATEGORIES = ["items"]
USAGE = "unduplify item <item>"
DESCRIPTION = """Unduplify the item with ID <item>, so that only one user may be holding it.

This undoes duplifying an item via the `duplify item` command.
You must own the item and it must be in your inventory in order to unduplify it.
All copies of the item in other users' inventories will disappear.

Ex. `duplify item 4`"""


def COMMAND(console, database, args):
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
    i = database.item_by_id(itemid)
    if i:
        # Make sure we are the item's owner.
        if console.user["name"] not in i["owners"] and not console.user["wizard"]:
            console.msg(NAME + ": you do not own this item")
            return False
        # Make sure we are holding the item.
        if itemid in console.user["inventory"] or console.user["wizard"]:
            # Unuplify the item.
            if not i["duplified"]:
                console.msg(NAME + ": item is already not duplified")
                return False
            i["duplified"] = False
            database.upsert_item(i)
            console.msg(NAME + ": done")

            # Delete item from all user inventories except ours, and all rooms.
            for u in console.router.users.values():
                if u["console"]["name"] == console.user["name"]:
                    # Not this user, this is us.
                    continue
                if itemid in u["console"].user["inventory"]:
                    u["console"].user["inventory"].remove(itemid)
                    u["console"].msg("{0} vanished from your inventory".format(i["name"]))
                    database.upsert_user(u["console"].user)
            for r in database.rooms.find():
                if itemid in r["items"]:
                    r["items"].remove(itemid)

            return True
        else:
            # We are not holding that item.
            console.msg(NAME + ": not holding item")
            return False

    else:
        # No item with that ID exists.
        console.msg(NAME + ": no such item")
        return False
