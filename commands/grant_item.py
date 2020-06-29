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
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        itemid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are holding the item.
    if itemid not in console.user["inventory"] and not console.user["wizard"]:
        console.msg(NAME + ": no such item in inventory")
        return False

    i = console.database.item_by_id(itemid)
    if not i:
        console.msg(NAME + ": no such item")
        return False

    # Make sure we are the item's owner.
    if console.user["name"] not in i["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this item")
        return False

    # Make sure the named user exists.
    u = console.database.user_by_name(args[1].lower())
    if not u:
        console.msg(NAME + ": no such user")
        return False

    # Check if the named user is already an owner.
    if args[1].lower() in i["owners"]:
        console.msg(NAME + ": user already an owner of this item")
        return False

    i["owners"].append(args[1].lower())
    console.database.upsert_item(i)
    console.msg(NAME + ": done")
    return True
