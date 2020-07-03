#####################
# Dennis MUD        #
# glue_item.py      #
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

NAME = "glue item"
CATEGORIES = ["items"]
USAGE = "glue item <item>"
DESCRIPTION = """Glue the item with ID <item>, so that once dropped, only owners can pick it up.

You must own the item and it must be in your inventory.
You can unglue a glued item with the `unglue item` command.

Ex. `glue item 4`"""


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

    # Check if the item is already glued.
    if thisitem["glued"]:
        console.msg("{0}: item is already glued".format(NAME))
        return False

    # Glue the item.
    thisitem["glued"] = True
    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
