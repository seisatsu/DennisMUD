#####################
# Dennis MUD        #
# drop.py           #
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

NAME = "drop"
CATEGORIES = ["items"]
USAGE = "drop <item>"
DESCRIPTION = """Drop the item called <item> into the current room. Also works by item ID.

Ex. `drop item crystal ball`
Ex2. `drop item 4`"""


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

    # Find the item in our inventory.
    for itemid in console.user["inventory"]:
        i = database.item_by_id(itemid)
        # Check for name or id match.
        if i["name"].lower() == name.lower() or str(i["id"]) == name:
            # Remove the item from our inventory and place it in the room.
            console.broadcast_room(console.user["nick"] + " dropped " + i["name"])
            if not i["duplified"] or not console.user["name"] in i["owners"]:
                # Only non-owners lose duplified items when dropping them.
                console.user["inventory"].remove(i["id"])
                if i["duplified"]:
                    # This will disappear.
                    console.broadcast_room(i["name"] + " vanished")
            if not i["duplified"] or (i["duplified"] and console.user["name"] in i["owners"]):
                # Only put unduplified items into the room unless we own them.
                if i["id"] not in thisroom["items"]:
                    # Account for duplified items.
                    thisroom["items"].append(i["id"])
                database.upsert_room(thisroom)
            database.upsert_user(console.user)
            return True

    console.msg(NAME + ": no such item in inventory")
    return False
