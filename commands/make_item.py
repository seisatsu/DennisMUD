#######################
# Dennis MUD          #
# make_item.py        #
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

NAME = "make item"
CATEGORIES = ["items"]
SCOST = 25
ALIASES = ["create item", "new item"]
USAGE = "make item <item_name>"
DESCRIPTION = """Create a new item called <item_name> and place it in your inventory.

You will be added as an owner of the new item.

Ex. `make item Crystal Ball`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"]):
        return False

    # Make sure the item name is not an integer, as this would be confusing.
    # We actually want an exception to be raised here.
    if len(args) == 1:
        try:
            int(args[0])
            console.msg("{0}: Item name cannot be an integer.".format(NAME))
            return False
        except ValueError:
            # Not an integer.
            pass

    # Get item name.
    itemname = ' '.join(args)
    if itemname == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Get a list of all items, sorted in reverse order.
    allitems = sorted(console.database.items.all(), reverse=True, key=lambda k: k["id"])

    # Make sure an item by this name does not already exist.
    for item in allitems:
        if item["name"].lower() == itemname.lower():
            console.msg("{0}: An item by this name already exists.".format(NAME))
            return False

    # Find the highest numbered currently existing item ID.
    if allitems:
        lastitem = allitems[0]["id"]
    else:
        lastitem = -1

    # Create our new item with an ID one higher than the last item.
    newitem = {
        "id": lastitem + 1,
        "name": itemname,
        "desc": "",
        "action": "",
        "lang" : None,
        "owners": [console.user["name"]],
        "glued": console.database.defaults["items"]["glued"],
        "hidden": False,
        "truehide": False,
        "chance": 1,
        "duplified": False,
        "container": {
            "enabled": False,
            "inventory": []
        },
        "telekey": None
    }

    # Add the new item to the our inventory, and save the item.
    console.user["inventory"].append(newitem["id"])
    console.database.upsert_user(console.user)
    console.database.upsert_item(newitem)

    # Show the item ID.
    console.msg("{0}: Done. (itemid: {1})".format(NAME, newitem["id"]))
    return True
