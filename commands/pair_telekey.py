#####################
# Dennis MUD        #
# pair_telekey.py   #
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

NAME = "pair telekey"
CATEGORIES = ["rooms", "items"]
USAGE = "pair telekey <item> <room>"
DESCRIPTION = """Make the <item> teleport its user to <room> when used.

You must own and be holding the item to pair it.
The destination room must be inbound unsealed, or you must be a room owner.
Any user who uses the item will teleport to the paired room.

Ex. `pair telekey 3 5` to make item 3 teleport the user to room 5."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=2):
        return False

    # Perform argument type checks and casts.
    itemid, roomid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int], [1, int]], retargs=[0, 1])
    if itemid is None or roomid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False

    # Lookup the destination room, and perform room checks.
    destroom = COMMON.check_room(NAME, console, roomid)
    if not destroom:
        return False

    # Make sure the destination room is not inbound sealed, or we are a room owner or a wizard.
    if destroom["sealed"]["inbound"] and not console.user["wizard"] and console.user["name"] not in destroom["owners"]:
        console.msg("{0}: The destination room is inbound sealed.".format(NAME))
        return False

    # Make sure the item is not already paired to a room.
    if thisitem["telekey"] is not None:
        console.msg("{0}: This item is already paired to a room.".format(NAME))
        return False

    # Pair the telekey.
    thisitem["telekey"] = roomid
    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
