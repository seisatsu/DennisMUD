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
    if len(args) < 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Get item name/id.
    name = ' '.join(args)

    # Look for the current room.
    thisroom = console.database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    found = None

    # Search for the item in the current room.
    for itemid in thisroom["items"]:
        i = console.database.item_by_id(itemid)
        # Check for name or id match.
        if i["name"].lower() == name.lower() or str(i["id"]) == name:
            found = i

    # Search for the item in our inventory.
    if found is None:
        for itemid in console.user["inventory"]:
            i = console.database.item_by_id(itemid)
            # Check for name or id match.
            if i["name"].lower() == name.lower() or str(i["id"]) == name:
                found = i

    # If the item was found, show the action.
    if found is not None:
        i = found
        if i["action"]:
            if "%player%" in i["action"]:
                action = i["action"].replace("%player%", console.user["nick"])
            else:
                action = console.user["nick"] + " " + i["action"]
            console.shell.broadcast_room(console, action)
        else:
            action = console.user["nick"] + " used " + i["name"]
            console.shell.broadcast_room(console, action)
        return True
    else:
        console.msg(NAME + ": no such item is here")
        return False
