#######################
# Dennis MUD          #
# unduplify_item.py   #
# Copyright 2019-2020 #
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

NAME = "unduplify item"
CATEGORIES = ["items"]
USAGE = "unduplify item <item_id>"
DESCRIPTION = """Unduplify the item <item_id>, so that it can only be in one place at a time.

This undoes duplifying an item via the `duplify item` command.
You must own the item and it must be in your inventory in order to unduplify it.
All copies of the item in other users' inventories will disappear.
Wizards can unduplify any item from anywhere, and it will appear in their inventory if not there already.

Ex. `duplify item 4`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Check if the item exists.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True)
    if not thisitem:
        return False

    # Check if the item is already not duplified.
    if not thisitem["duplified"]:
        console.msg("{0}: This item is already not duplified.".format(NAME))
        return False

    # Make sure we are holding the item or we are a wizard.
    # If we are a wizard but aren't holding the item, put it in our inventory,
    # Because otherwise it won't have any locations.
    if itemid not in console.user["inventory"] and not console.user["wizard"]:
        console.msg("{0}: You are not holding the item.".format(NAME))
        return False
    elif console.user["wizard"] and itemid not in console.user["inventory"]:
        console.user["inventory"].append(itemid)
        console.database.upsert_user(console.user)
        console.msg("{0} appeared in your inventory.".format(COMMON.format_item(NAME, thisitem["name"], upper=True)))

    # Delete the item from all user inventories except ours, and announce its disappearance.
    for user in console.router.users.values():
        if user["console"].user["name"] == console.user["name"]:
            # Not this user, this is us.
            continue
        if itemid in user["console"].user["inventory"]:
            user["console"].user["inventory"].remove(itemid)
            user["console"].msg("{0} vanished from your inventory.".format(
                COMMON.format_item(NAME, thisitem["name"], upper=True)))
            console.database.upsert_user(user["console"].user)

    # Delete the item from all rooms.
    for room in console.database.rooms.all():
        if itemid in room["items"]:
            room["items"].remove(itemid)
            console.database.upsert_room(room)

    # Unduplify the item.
    thisitem["duplified"] = False
    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
