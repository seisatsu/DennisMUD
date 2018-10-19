#####################
# Dennis MUD        #
# locate_item.py    #
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

NAME = "locate item"
CATEGORIES = ["items"]
USAGE = "locate item <id>"
DESCRIPTION = """Find out what room the item <id> is in, or who is holding it.

You can only locate an item that you own.

Ex. `locate item 4`"""


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

    i = database.item_by_id(itemid)
    if not i:
        console.msg(NAME + ": no such item")
        return False

    # Make sure we are the item's owner.
    if console.user["name"] not in i["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this item")
        return False

    # check if we are holding the item.
    if itemid in console.user["inventory"]:
        console.msg("Item " + i["name"] + " (" + str(i["id"]) + ") is in your inventory")
        return True

    # check if someone else is holding the item.
    for u in database.users.find():
        if itemid in u["inventory"]:
            console.msg("Item " + i["name"] + " (" + str(i["id"]) + ") is in " + u["name"] + "'s your inventory")
            return True

    # check if the item is in a room.
    for r in database.rooms.find():
        if itemid in r["items"]:
            console.msg("Item " + i["name"] + " (" + str(i["id"]) + ") is in room " +
                        r["name"] + " (" + str(r["id"]) + ")")
            return True

    # Couldn't find the item.
    console.msg(NAME + ": Warning: item exists but could not be found")
    return False
