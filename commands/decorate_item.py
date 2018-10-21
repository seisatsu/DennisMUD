#####################
# Dennis MUD        #
# decorate_item.py  #
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

NAME = "decorate item"
CATEGORIES = ["items"]
USAGE = "decorate item <id> <action>"
DESCRIPTION = """Set a custom <action> to display when a player uses the item <id>.

By default, the action text is shown following the player's nickname and one space.
To place the player's name elsewhere in the text, use the %player% marker.
You must own the item and be holding it in order to decorate it.
You can remove the custom action from an item with the `undecorate item` command.

Ex. `decorate item 4 holds the green orb, and it begins to glow.`
Ex2. `decorate item 4 The green orb glows in %player%'s hand.`"""


def COMMAND(console, database, args):
    if len(args) < 2:
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

    # Make sure we are holding the item.
    if itemid not in console.user["inventory"] and not console.user["wizard"]:
        console.msg(NAME + ": no such item in inventory")
        return False

    # Make sure the item exists.
    i = database.item_by_id(itemid)
    if not i:
        console.msg(NAME + ": no such item")
        return False

    # Make sure we are the item's owner.
    if console.user["name"] not in i["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this item")
        return False

    i["action"] = ' '.join(args[1:])
    database.upsert_item(i)
    console.msg(NAME + ": done")
    return True
