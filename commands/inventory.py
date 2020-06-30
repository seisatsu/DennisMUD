#####################
# Dennis MUD        #
# inventory.py      #
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

NAME = "inventory"
CATEGORIES = ["items"]
ALIASES = ["inv"]
USAGE = "inventory"
DESCRIPTION = "List all items in your inventory."


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Check if our inventory is empty.
    if not console.user["inventory"]:
        console.msg(NAME + ": empty")

    # Enumerate our inventory.
    for itemid in console.user["inventory"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid, reason=False)

        # Uh oh, an item in our inventory doesn't actually exist.
        if not thisitem:
            console.log.error("inventory item does not exist for user: {user} ({item})", user=console.user["name"],
                              item=itemid)
            console.msg("{0}: error: inventory item does not exist: {1}".format(NAME, itemid))
            continue

        # Show the item's name and ID.
        console.msg("{0} ({1})".format(thisitem["name"], itemid))

    # Finished.
    return True
