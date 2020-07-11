#######################
# Dennis MUD          #
# break_item.py       #
# Copyright 2018-2020 #
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

NAME = "break item"
CATEGORIES = ["items"]
ALIASES = ["delete item", "destroy item", "remove item"]
USAGE = "break item <item_id>"
DESCRIPTION = """Break the item in your inventory with ID <item_id>.

You must an owner of the item, and it must be in your inventory.
Wizards can break any item from anywhere.

Ex. `break item 4` to break the item with ID 4."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False

    # Delete the item from the database.
    console.database.delete_item(thisitem)

    # The item is duplified, so start by deleting it from every user's inventory.
    if thisitem["duplified"]:
        for user in console.router.users.values():
            try:  # Trap to catch a rare crash
                if itemid in user["console"].user["inventory"]:
                    user["console"].user["inventory"].remove(itemid)
                    user["console"].msg("{0} vanished from your inventory.".format(thisitem["name"]))
                    console.database.upsert_user(user["console"].user)
            except:
                with open('break_item_trap.txt', 'w') as file:
                    file.write("itemid: {0}, u: {1}".format(str(itemid), user))
                    file.write("console: {0}".format(user["console"]))
                    file.write("user: {0}".format(user["console"].user))

    # If the item is duplified or we are a wizard, check all rooms for the presence of the item, and delete.
    if thisitem["duplified"] or console.user["wizard"]:
        for room in console.database.rooms.all():
            if itemid in room["items"]:
                room["items"].remove(itemid)
                console.database.upsert_room(room)

    # It's still in our inventory, so it must not have been duplified. Delete it from our inventory now.
    if itemid in console.user["inventory"] and not thisitem["duplified"]:
        console.user["inventory"].remove(itemid)
        console.msg("{0} vanished from your inventory.".format(thisitem["name"]))
        console.database.upsert_user(console.user)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True

