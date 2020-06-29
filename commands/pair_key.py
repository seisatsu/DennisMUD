#####################
# Dennis MUD        #
# pair_key.py       #
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

NAME = "pair key"
CATEGORIES = ["exits", "items"]
USAGE = "pair key <exit> <item>"
DESCRIPTION = """Make the locked <exit> in this room passable by anyone holding <item>.

You must own and be holding the item, and you must also own the exit or its room.
Any user who holds the item will be able to pass through the locked exit as if it is unlocked.

Ex. `pair key 4 3` to make exit 4 unlock with item 3."""


def COMMAND(console, args):
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Make sure the exit and item IDs are both integers.
    try:
        exitid = int(args[0])
        itemid = int(args[1])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure the item exists.
    i = console.database.item_by_id(itemid)
    if not i:
        console.msg(NAME + ": no such item")
        return False

    # Make sure we are holding the item.
    if itemid not in console.user["inventory"] and not console.user["wizard"]:
        console.msg(NAME + ": no such item in inventory")
        return False

    # Make sure the exit is in this room.
    thisroom = console.database.room_by_id(console.user["room"])
    if thisroom:
        if exitid > len(thisroom["exits"])-1 or exitid < 0:
            console.msg(NAME + ": no such exit")
            return False
        if not thisroom["exits"][exitid]["locked"]:
            console.msg(NAME + ": only locked exits can have keys")
            return False
        if thisroom["exits"][exitid]["key"]:
            console.msg(NAME + ": this exit is already paired to a key")
            return False
        if console.user["name"] not in i["owners"] and not console.user["wizard"]:
            console.msg(NAME + ": you do not own this item")
            return False
        if console.user["name"] not in thisroom["exits"][exitid]["owners"] \
                and console.user["name"] not in thisroom["owners"] and not console.user["wizard"]:
            console.msg(NAME + ": you do not own this exit or this room")
            return False
        thisroom["exits"][exitid]["key"] = itemid
        console.database.upsert_room(thisroom)
        console.msg(NAME + ": done")
        return True
    console.msg("warning: current room does not exist")
    return False
