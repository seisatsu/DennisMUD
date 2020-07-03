#####################
# Dennis MUD        #
# pair_key.py       #
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

NAME = "pair key"
CATEGORIES = ["exits", "items"]
USAGE = "pair key <exit> <item>"
DESCRIPTION = """Make the locked <exit> in this room passable by anyone holding <item>.

You must own and be holding the item, and you must also own the exit or its room.
Any user who holds the item will be able to pass through the locked exit as if it is unlocked.

Ex. `pair key 4 3` to make exit 4 unlock with item 3."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=2):
        return False

    # Perform argument type checks and casts.
    exitid, itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int], [1, int]], retargs=[0, 1])
    if exitid is None or itemid is None:
        return False

    # Lookup the current room, and perform exit checks.
    thisroom = COMMON.check_exit(NAME, console, exitid, owner=True)
    if not thisroom:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False

    # Make sure the exit is locked.
    if not thisroom["exits"][exitid]["locked"]:
        console.msg("{0}: Only locked exits can have keys.".format(NAME))
        return False

    # Make sure the exit is not already paired to a key.
    if thisroom["exits"][exitid]["key"]:
        console.msg("{0}: This exit is already paired to a key.".format(NAME))
        return False

    # Pair the key.
    thisroom["exits"][exitid]["key"] = itemid
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
