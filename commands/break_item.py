#####################
# Dennis MUD        #
# break_item.py     #
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

NAME = "break item"
CATEGORIES = ["items"]
ALIASES = ["delete item", "destroy item", "remove item"]
USAGE = "break item <item>"
DESCRIPTION = """Break the item in your inventory with ID <item>.

You must an owner of the item, and it must be in your inventory.

Ex. `break item 4` to break the item with ID 4."""


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
            # Delete the item and remove it from our inventory.
            database.delete_item(i)
            if i["duplified"]:
                # Duplified items disappear from everyone's inventory and every room when broken.
                for u in console.router.users.values():
                    try: # Trap to catch rare crash
                        if itemid in u["console"].user["inventory"]:
                            u["console"].user["inventory"].remove(itemid)
                            u["console"].msg("{0} vanished from your inventory".format(i["name"]))
                            database.upsert_user(u["console"].user)
                    except:
                        with open('break_item_trap.txt', 'w') as file:
                            file.write("itemid: {0}, u: {1}".format(str(itemid), u))
                            file.write("console: {0}".format(u["console"]))
                            file.write("user: {0}".format(u["console"].user))
                for r in database.rooms.all():
                    if itemid in r["items"]:
                        r["items"].remove(itemid)
            else:
                # It's not duplified, so we only have to worry about our own inventory.
                console.user["inventory"].remove(itemid)
                console.msg("{0} vanished from your inventory".format(i["name"]))
                database.upsert_user(console.user)
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
