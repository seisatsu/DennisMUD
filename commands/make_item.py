#####################
# Dennis MUD        #
# make_item.py      #
# Copyright 2018    #
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

NAME = "make item"
CATEGORIES = ["items"]
USAGE = "make item <name>"
DESCRIPTION = """Create a new item called <name> and place it in your inventory.

You will be added as an owner of the new item.

Ex. `make item Crystal Ball`"""


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Get name.
    name = ' '.join(args)

    # Make sure the name is not an integer, as this would be confusing.
    try:
        test = int(name)
        console.msg(NAME + ": item name cannot be an integer")
        return False
    except ValueError:
        # Not an integer.
        pass

    # Check if an item by this name already exists. Case insensitive.
    items = list(database.items.find().sort("id", -1))
    if items:
        for i in items:
            if i["name"].lower() == name.lower():
                console.msg(NAME + ": an item by this name already exists")
                return False  # An item by this name already exists.

    # Find the highest numbered currently existing item ID.
    if items:
        lastitem = items[0]["id"]
    else:
        lastitem = -1

    # Create our new item with an ID one higher.
    newitem = {
        "id": lastitem + 1,
        "name": name,
        "desc": "",
        "action": "",
        "owners": [console.user["name"]],
        "glued": database.defaults["items"]["glued"],
        "duplified": False
    }

    # Add the item to the creator's inventory.
    console.user["inventory"].append(newitem["id"])
    database.upsert_user(console.user)

    # Save.
    database.upsert_item(newitem)
    console.msg(NAME + ": done (id: " + str(newitem["id"]) + ")")
    return True
