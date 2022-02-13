#######################
# Dennis MUD          #
# randomize_item.py        #
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

NAME = "randomize item"
CATEGORIES = ["items"]
USAGE = "randomize item <item_id>"
DESCRIPTION = """Set the chance of the item <item_id> appearing in the room.

You must own the item in order to randomize it.
Wizards can randomize any item and also see them all the time.
Chance is optional, without giving a chance it just shows you the currently set one.
Taking an item from the ground currently sets the randomize chance back to 1.

Ex. `randomize item 3` shows you the chance for id 3.
Ex2. `randomize item 3 1 (100% chance)`
Ex3. `randomize item 3 10 (10% chance)`
Ex4. `randomize item 3 100 (1% chance)`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1, argmax=2):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False
    # Lookup the target item and perform item checks.
    if len(args)==2:
        itemchance = COMMON.check_argtypes(NAME, console, args, checks=[[1, int]], retargs=1)
        if itemchance is None:
            return False


    if len(args)<2:
        console.msg("That item has a 1 out of {0} chance to appear.".format(thisitem["chance"]))
    else:    
        if itemchance<1:
            console.msg("{0}: Chance must be greater than 0.".format(NAME))
            return False
        thisitem["chance"] = itemchance
        thisitem["hidden"] = False

    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
