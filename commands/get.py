#####################
# Dennis MUD        #
# get.py            #
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

NAME = "get"
CATEGORIES = ["items"]
USAGE = "get <item>"
DESCRIPTION = """Pick up the item called <item> from the current room. Also works by item ID.

Ex. `get item crystal ball`
Ex2. `get item 4`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Lookup the current room.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # Get item name/id.
    name = ' '.join(args)

    # Search the current room for the target item.
    for itemid in thisroom["items"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid)
        if not thisitem:
            return False

        # Check for name or id match.
        if thisitem["name"].lower() == name.lower() or str(thisitem["id"]) == name:
            console.shell.broadcast_room(console, console.user["nick"] + " picked up " + thisitem["name"])

            # The item is glued down. Only the owner or a wizard can pick it up.
            if thisitem["glued"] and console.user["name"] not in thisitem["owners"] and not console.user["wizard"]:
                console.msg(NAME + ": you cannot get this item")
                return False

            # Don't remove duplified items when picking them up, unless we are the owner.
            if console.user["name"] in thisitem["owners"] or not thisitem["duplified"]:
                thisroom["items"].remove(thisitem["id"])

            # If the item is not in our inventory yet, add it.
            if thisitem["id"] not in console.user["inventory"]:
                console.user["inventory"].append(thisitem["id"])

            # Update the room and user documents.
            console.database.upsert_room(thisroom)
            console.database.upsert_user(console.user)

            # Finished.
            return True

    # The item wasn't found in the room.
    console.msg(NAME + ": no such item in room")
    return False
