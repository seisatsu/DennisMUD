#######################
# Dennis MUD          #
# rename_item.py      #
# Copyright 2018-2020 #
# Michael D. Reiley   #
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

NAME = "rename item"
CATEGORIES = ["items"]
USAGE = "rename item <id> <name>"
DESCRIPTION = """Set the name of the item <id> which you are holding to <name>.

You must own the item and it must be in your inventory.

Ex. `rename item 4 Blue Shard`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False

    # Make sure the item name is not an integer, as this would be confusing.
    # We actually want an exception to be raised here.
    if len(args) == 2:
        try:
            int(args[1])
            console.msg("{0}: The item name cannot be an integer.".format(NAME))
            return False
        except ValueError:
            # Not an integer.
            pass

    # Get new item name.
    itemname = ' '.join(args[1:])
    if itemname == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Make sure an item by this name does not already exist.
    # Make an exception if that is the item we are renaming. (changing case)
    for item in console.database.items.all():
        if item["name"].lower() == itemname.lower() and item["name"].lower() != thisitem["name"].lower():
            console.msg("{0}: An item by that name already exists.".format(NAME))
            return False

    # Rename the item.
    thisitem["name"] = itemname
    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
