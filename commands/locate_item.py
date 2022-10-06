#######################
# Dennis MUD          #
# locate_item.py      #
# Copyright 2018-2020 #
# Sei Satzparad       #
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

NAME = "locate item"
CATEGORIES = ["items"]
ALIASES = ["find item"]
USAGE = "locate item <item_id>"
DESCRIPTION = """Find out what room the item <item_id> is in, or who is holding it.

You can only locate an item that you own.
Wizards can locate any item.

Ex. `locate item 4`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Check if the item exists.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=False)
    if not thisitem:
        return False

    # Keep track of whether we found anything in case the item is duplified and we can't return right away.
    found_something = False

    # Check if we are holding the item.
    if itemid in console.user["inventory"]:
        console.msg("{0}: {1} ({2}) is in your inventory.".format(NAME, thisitem["name"], thisitem["id"]))
        # If the item is duplified we need to keep looking for other copies.
        if not thisitem["duplified"]:
            return True
        found_something = True

    # Check if someone else is holding the item.
    for targetuser in console.database.users.all():
        if targetuser["name"] == console.user["name"]:
            continue
        if itemid in targetuser["inventory"]:
            console.msg("{0}: {1} ({2}) is in the inventory of: {3}.".format(NAME, thisitem["name"], thisitem["id"],
                                                                           targetuser["name"]))
            # If the item is duplified we need to keep looking for other copies.
            if not thisitem["duplified"]:
                return True
            found_something = True

    # Check if the item is in a room.
    for targetroom in console.database.rooms.all():
        if itemid in targetroom["items"]:
            console.msg("{0}: {1} ({2}) is in room: {3} ({4})".format(NAME, thisitem["name"], thisitem["id"],
                                                                     targetroom["name"], targetroom["id"]))
            # If the item is duplified we need to keep looking for other copies.
            if not thisitem["duplified"]:
                return True
            found_something = True

    # Couldn't find the item.
    if not found_something:
        console.log.error("Item exists but has no location: {item}", item=itemid)
        console.msg("{0}: ERROR: Item exists but has no location. Use `requisition` to fix this.".format(NAME))
        return False

    # Finished.
    return True
