#####################
# Dennis MUD        #
# duplify_item.py   #
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

NAME = "duplify item"
CATEGORIES = ["items"]
USAGE = "duplify item <item_id>"
DESCRIPTION = """Duplify the item with <item_id>, so that any number of people can pick it up.

When a user besides the owner `get`s a duplified item, it doesn't disappear from the room it is in.
Any number of users may be holding the duplified item.
When the owner uses `break item` on a duplified item, all copies will break.
When a user besides the owner drops a duplified item, it will vanish.
Duplified items exist permanently in the owner's inventory until broken, and can be dropped in multiple places.
This feature is particularly useful for keys.
You can undo this with the `unduplify item` command.
You must own the item and it must be in your inventory in order to duplify it.
Wizards can duplify any item.

Ex. `duplify item 4`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False

    # Check if the item is already duplified.
    if thisitem["duplified"]:
        console.msg("{0}: This item is already duplified.".format(NAME))
        return False

    # Duplify the item.
    thisitem["duplified"] = True
    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
