#####################
# Dennis MUD        #
# list_items.py     #
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

NAME = "list items"
CATEGORIES = ["items"]
USAGE = "list items"
DESCRIPTION = """List all items in the world that you own.

If you are a wizard, you will see a list of all items that exist."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Sort all items in the database by ID.
    allitems = sorted(console.database.items.all(), key=lambda k: k["id"])

    # Iterate through the items, checking whether we own each one (or are a wizard),
    # and keeping track of how many items we found.
    itemcount = 0
    for thisitem in allitems:
        # We either own this item, or we are a wizard. List it out.
        if console.user["name"] in thisitem["owners"] or console.user["wizard"]:
            console.msg("{0} ({1})".format(thisitem["name"], thisitem["id"]))
            itemcount += 1

    # We found nothing. If we are a wizard, that means no items exist. Otherwise, it means we don't own any.
    if not itemcount:
        if console.user["wizard"]:
            console.msg("{0}: There are no items.".format(NAME))
        else:
            console.msg("{0}: You do not own any items.".format(NAME))

    # Report how many we found.
    else:
        console.msg("{0}: Total items: {1}".format(NAME, itemcount))
    return True
