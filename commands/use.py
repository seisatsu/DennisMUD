#####################
# Dennis MUD        #
# use.py            #
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

NAME = "use"
CATEGORIES = ["items"]
USAGE = "use <item>"
DESCRIPTION = """Broadcast the custom action, if any, for the <item> in the current room or your inventory.

This will hopefully do more some day.

Ex. `use 4` to show the custom action for item 4.
Ex2. `use Crystal Ball` to show the custom action for the item named "Crystal Ball"."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Get item name or id.
    itemname = ' '.join(args)

    # Reference to whatever item we do or don't find in the room.
    targetitem = None

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # Search for the item in our inventory.
    for itemid in console.user["inventory"]:
        testitem = console.database.item_by_id(itemid)
        # A reference was found to a nonexistent item. Report this and quietly continue searching.
        if not testitem:
            console.log.error("reference exists to nonexistent item: {item}", item=itemid)
            continue

        # Check for name or id match.
        if testitem["name"].lower() == itemname.lower() or str(testitem["id"]) == itemname:
            targetitem = testitem
            break

    # We didn't find it in our inventory, so search for the item in the current room.
    if not targetitem:
        for itemid in thisroom["items"]:
            testitem = console.database.item_by_id(itemid)
            # A reference was found to a nonexistent item. Report this and quietly continue searching.
            if not testitem:
                console.log.error("reference exists to nonexistent item: {item}", item=itemid)
                continue

            # Check for name or id match.
            if testitem["name"].lower() == itemname.lower() or str(testitem["id"]) == itemname:
                targetitem = testitem
                break

    # If the item was found, show the action.
    if targetitem:
        # This item has a custom action.
        if targetitem["action"]:
            # Format a custom item action containing a player tag.
            if "%player%" in targetitem["action"]:
                action = targetitem["action"].replace("%player%", console.user["nick"])

            # Format a regular custom item action.
            else:
                action = "{0} {1}".format(console.user["nick"], targetitem["action"])

            # Broadcast the custom action.
            console.shell.broadcast_room(console, action)

        # This item has no custom action. Broadcast the default action.
        else:
            action = "{0} used {1}".format(console.user["nick"], targetitem["name"])
            console.shell.broadcast_room(console, action)
        return True

    # We didn't find anything.
    else:
        console.msg("{0}: no such item is here: {1}".format(NAME, itemname))
        return False
