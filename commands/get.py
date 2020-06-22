#####################
# Dennis MUD        #
# get.py            #
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

NAME = "get"
CATEGORIES = ["items"]
USAGE = "get <item>"
DESCRIPTION = """Pick up the item called <item> from the current room. Also works by item ID.

Ex. `get item crystal ball`
Ex2. `get item 4`"""


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Look for the current room.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    # Get item name/id.
    name = ' '.join(args)

    # Find the item in the current room.
    for itemid in thisroom["items"]:
        i = database.item_by_id(itemid)
        # Check for name or id match.
        if i["name"].lower() == name.lower() or str(i["id"]) == name:
            if i["glued"] and console.user["name"] not in i["owners"] and not console.user["wizard"]:
                # The item is glued down. Only the owner can pick it up.
                console.msg(NAME + ": you cannot get this item")
                return False
            # Remove the item from the room and place it in our inventory.
            if console.user["name"] in i["owners"] or not i["duplified"]:
                # Don't remove duplified items when picking them up, unless we are the owner.
                thisroom["items"].remove(i["id"])
            if i["id"] not in console.user["inventory"]:
                # Account for duplified items.
                console.user["inventory"].append(i["id"])
            database.upsert_room(thisroom)
            database.upsert_user(console.user)
            console.broadcast_room(console.user["nick"] + " picked up " + i["name"])
            return True

    console.msg(NAME + ": no such item in room")
    return False
