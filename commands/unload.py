#######################
# Dennis MUD          #
# put_into.py             #
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

NAME = "unload"
CATEGORIES = ["items"]
USAGE = "unload <item> from <container>"
DESCRIPTION = """unload the item called <item> from the <container>.

You may use a full or partial item name, or the item ID.

Ex. `unload 4 from bag`
Ex2. `unload a coffee from the large chest`"""


def COMMAND(console, args):

    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=3):
        return False

    # Iterate through the args to split it into two
    thisitemname=[]
    thiscontainername=[]
    sw=0
    for ar in args:
        if ar=="from":
            sw=1
        elif sw==0: thisitemname.append(ar)
        elif sw==1: thiscontainername.append(ar)
    thisitemname=' '.join(thisitemname)
    thiscontainername=' '.join(thiscontainername)


    # Get item name/id.
    target = thiscontainername.lower()
    if target == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    
    # Search our inventory for the target item.
    for containerid in console.user["inventory"]:
        # Lookup the target item and perform item checks.
        thiscontainer = COMMON.check_item(NAME, console, containerid, reason=False)
        # Lookup the current container.
        if not thiscontainer:
            console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"], item=containerid)
            console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, containerid))
            continue

        # Check for name or id match. Also check if the user prepended "the ". Figure out how to put into it.
        if thiscontainername in [thiscontainer["name"].lower(), "the " + thiscontainer["name"].lower()] or str(thiscontainer["id"]) == thiscontainername:
            # Found the container, but do they have the item too?
            for itemid in thiscontainer["container"]["inventory"]:
                # Lookup the target item and perform item checks.
                thisitem = COMMON.check_item(NAME, console, itemid, reason=False)
                # Lookup the current container.
                if not thisitem:
                    console.log.error("Item referenced in container does not exist: {room} :: {item}", room=console.user["room"], item=itemid)
                    console.msg("{0}: ERROR: Item referenced in this container does not exist: {1}".format(NAME, itemid))
                    continue
                if thisitemname in [thisitem["name"].lower(), "the " + thisitem["name"].lower()] or str(thisitem["id"]) == thisitemname:
                    # We found both! Time to put that item into the container.
                    
                    
                    thiscontainer["container"]["inventory"].remove(thisitem["id"])

                    # Only put unduplified items into the container unless we are the owner.
                    if not thisitem["duplified"] or console.user["name"] in thisitem["owners"]:
                        # If the item is not in the room yet, add it.
                        if thisitem["id"] in console.user["inventory"]:
                            console.msg("{0}: This item is already in your inventory.".format(NAME))
                        else:
                            console.user["inventory"].append(thisitem["id"])
                            console.shell.broadcast_room(console, "{0} has took {1} from {2}.".format(
                                console.user["nick"], COMMON.format_item(NAME, thisitem["name"]),COMMON.format_item(NAME, thiscontainer["name"])))

                        # Update the room document.
                        console.database.upsert_item(thiscontainer)

                    # Update the user document.
                    console.database.upsert_user(console.user)
                else:
                    console.msg("Couldn't find {0} in the {1}.".format(thisitemname,thiscontainername))
            # Finished.
            return True

    # We didn't find the requested item. Check for a partial match.
    partial = COMMON.match_partial(NAME, console, target, "item", room=False, inventory=True)
    if partial:
        return COMMAND(console, partial)

    # Maybe the user accidentally typed "put into item <item>".
    if args[0].lower() == "item":
        console.msg("{0}: Maybe you meant \"unload {1}\".".format(NAME, ' '.join(args[1:])))

    return False
