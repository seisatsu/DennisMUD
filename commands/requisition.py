#####################
# Dennis MUD        #
# requisition.py    #
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

NAME = "requisition"
CATEGORIES = ["items"]
USAGE = "requisition <item>"
DESCRIPTION = """Obtain the item with id <item>, regardless of where it is.

Whether the item is in another room or someone else's inventory, it will be moved to your inventory.
You can only requisition an item that you own.

Ex. `requisition 14` to move item 14 to your inventory."""


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
        if console.user["name"] not in i["owners"] and not console.user["wizard"]:
            console.msg(NAME + ": you do not have permission to requisition that item")
            return False

        # If the item is in a room's item list, remove it.
        rooms = database.rooms.find()
        if rooms:
            for r in rooms:
                if itemid in r["items"] and not i["duplified"]:
                    # Don't remove duplified items from their rooms.
                    r["items"].remove(itemid)
                    database.upsert_room(r)

        # If the item is in someone's inventory, remove it.
        for u in console.router.users.values():
            if itemid in u["console"].user["inventory"]:
                u["console"].user["inventory"].remove(itemid)
                u["console"].msg("{0} vanished from your inventory".format(i["name"]))
                database.upsert_user(u["console"].user)

        # Place the item in our inventory.
        console.user["inventory"].append(itemid)
        database.upsert_user(console.user)
        console.msg("requisitioned item " + i["name"] + " (" + str(i["id"]) + ")")
        console.msg("{0} appeared in your inventory".format(i["name"]))
        return True

    else:
        # No item with that ID exists.
        console.msg(NAME + ": no such item")
        return False
