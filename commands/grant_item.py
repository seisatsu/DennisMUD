#####################
# Dennis MUD        #
# grant_item.py     #
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

NAME = "grant item"
CATEGORIES = ["items"]
ALIASES = ["share item"]
USAGE = "grant item <id> <username>"
DESCRIPTION = """Add user <username> to the owners of item <id>.

You must own the item in order to grant it to another user. You will also retain ownership.
You can revoke ownership with the `revoke item` command, provided you are an owner.

Ex. `grant item 4 seisatsu`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=2):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False

    # Make sure the named user exists.
    targetuser = COMMON.check_user(NAME, console, args[1].lower())
    if not targetuser:
        return False

    # Check if the named user is already an owner.
    if args[1].lower() in thisitem["owners"]:
        console.msg("{0}: user already an owner of this item".format(NAME))
        return False

    # Grant the item to the user.
    thisitem["owners"].append(args[1].lower())
    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
