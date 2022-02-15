#######################
# Dennis MUD          #
# remake_item.py      #
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

NAME = "remake item"
CATEGORIES = ["items"]
USAGE = "remake item <item_id>"
DESCRIPTION = """Resets the item <item_id> in this room.

Name and owner list are untouched.
You must own the item or its room.
Wizards can remake any item.

Ex. `remake item 3`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1, argmax=1):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False

    # remake the item.
    thisitem["desc"] = ""
    thisitem["action"] = ""
    thisitem["lang"] = None
    thisitem["glued"] = console.database.defaults["items"]["glued"]
    thisitem["hidden"] = False
    thisitem["truehide"] = False
    thisitem["chance"] = 1
    thisitem["duplified"] = False
    thisitem["container"]["enabled"] = False
    thisitem["container"]["inventory"] = []
    thisitem["telekey"] = None
    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True

