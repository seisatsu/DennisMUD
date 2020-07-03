#####################
# Dennis MUD        #
# lock.py           #
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

NAME = "look"
CATEGORIES = ["exploration"]
ALIASES = ["look at"]
USAGE = "look [name]"
DESCRIPTION = """Look at the current room or the named object or user.

If used by itself without any arguments, this command gives information about the current room.
Otherwise, you can look at yourself, an item in the room or your inventory, or an exit.
You can also look at a user by their username or their nickname.

Ex. `look` to look at the current room.
Ex2. `look self` to look at yourself.
Ex3. `look crystal ball` to look at the item "crystal ball"."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console)
    if not thisroom:
        return False

    # There were no arguments, so just look at the current room.
    if len(args) == 0:
        # Show the room name, ID, owners, and description.
        console.msg("{0} ({1})".format(thisroom["name"], thisroom["id"]))
        console.msg("Owned by: {0}".format(', '.join(thisroom["owners"])))
        if thisroom["desc"]:
            console.msg(thisroom["desc"])

        # Build and show the user list.
        userlist = []
        for user in thisroom["users"]:
            userlist.append(console.database.user_by_name(user)["nick"])
        console.msg("Occupants: {0}".format(", ".join(userlist)))

        # Build and show the item list.
        itemlist = []
        for itemid in thisroom["items"]:
            item = console.database.item_by_id(itemid)
            if item:
                itemlist.append("{0} ({1})".format(item["name"], item["id"]))
        if itemlist:
            console.msg("Items: {0}".format(", ".join(itemlist)))

        # Build and show the exit list.
        exitlist = []
        for ex in range(len(thisroom["exits"])):
            exitlist.append("{0} ({1})".format(thisroom["exits"][ex]["name"], ex))
        if exitlist:
            console.msg("Exits: {0}".format(", ".join(exitlist)))
        return True

    # There were arguments. Figure out what in the room they might be referring to.
    # Also keep track of whether we found anything, and whether we found a certain item
    # in the current room so we don't list it twice if it was duplified and also in our inventory.
    else:
        # See if the user tried to look at an ID instead of a name.
        try:
            int(' '.join(args))
            console.msg("{0}: Requires a name, not an ID.".format(NAME))
            return False

        # Nope, just looking for something that isn't there.
        except:
            pass

        # Keep track of whether we found stuff during our search.
        found_something = False
        found_item = None

        # Looking at ourselves. Show user nickname real name, and description.
        if len(args) == 1 and args[0].lower() == "self":
            console.msg("{0} ({1})".format(console.user["nick"], console.user["name"]))

            # Description exists, so show it.
            if console.user["desc"]:
                console.msg(console.user["desc"])
            return True

        # It wasn't us, so maybe it's an item in the room.
        for itemid in thisroom["items"]:
            item = console.database.item_by_id(itemid)
            # A reference was found to a nonexistent item. Report this and continue searching.
            if not item:
                console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                                  item=itemid)
                console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
                continue
            attributes = []

            # It was an item in the room. Show the item's name, ID, owners, description, and attributes.
            if item and item["name"].lower() == ' '.join(args).lower():
                # Only enumerate item attributes if we are the item owner or a wizard.
                if console.user["name"] in item["owners"] or console.user["wizard"]:
                    if item["duplified"]:
                        attributes.append("[duplified]")
                    if item["glued"]:
                        attributes.append("[glued]")
                    if item["telekey"]:
                        attributes.append("[telekey:{0}]".format(item["telekey"]))

                # Send the info for this item.
                console.msg("{0} ({1}) {2}".format(item["name"], item["id"], ' '.join(attributes)))
                console.msg("Owned by: {0}".format(', '.join(item["owners"])))

                # Description exists, so show it.
                if item["desc"]:
                    console.msg(item["desc"])
                found_something = True
                found_item = itemid
                break

        # Maybe it's an item in our inventory.
        for itemid in console.user["inventory"]:
            item = console.database.item_by_id(itemid)
            # A reference was found to a nonexistent item. Report this and continue searching.
            if not item:
                console.log.error("Item referenced in user inventory does not exist: {user} :: {item}",
                                  user=console.user["name"], item=itemid)
                console.msg("{0}: ERROR: Item referenced in your inventory does not exist: {1}".format(NAME, itemid))
                continue
            attributes = []

            # It was an item in our inventory. Show the item's name, ID, owners, description, and attributes,
            # but only if we didn't already see it in the current room.
            if item and item["name"].lower() == ' '.join(args).lower() and item["id"] != found_item:
                # Only enumerate item attributes if we are the item owner or a wizard.
                if console.user["name"] in item["owners"] or console.user["wizard"]:
                    if item["duplified"]:
                        attributes.append("[duplified]")
                    if item["glued"]:
                        attributes.append("[glued]")
                    if item["telekey"]:
                        attributes.append("[telekey:{0}]".format(item["telekey"]))

                # Send the info for this item.
                console.msg("{0} ({1}) {2}".format(item["name"], item["id"], ' '.join(attributes)))
                console.msg("Owned by: {0}".format(', '.join(item["owners"])))

                # Description exists, so show it.
                if item["desc"]:
                    console.msg(item["desc"])  # Print item description.
                found_something = True
                break

        # Maybe it's an exit in the room.
        for ex in range(len(thisroom["exits"])):
            if thisroom["exits"][ex]["name"].lower() == ' '.join(args).lower():
                # It was an exit in the current room. Show the exit name, destination,
                # description, ID, owners, and any key information.
                console.msg("{0} ({1}) -> {2}".format(thisroom["exits"][ex]["name"], ex, thisroom["exits"][ex]["dest"]))
                console.msg("Owned by: {0}".format(', '.join(thisroom["exits"][ex]["owners"])))

                # Description exists, so show it.
                if thisroom["exits"][ex]["desc"]:
                    console.msg(thisroom["exits"][ex]["desc"])

                # Key info is visible or we own the exit or are a wizard, so show it.
                if thisroom["exits"][ex]["key"] and (console.user["name"] in thisroom["exits"][ex]["owners"]
                                                     or console.user["wizard"]
                                                     or not thisroom["exits"][ex]["key_hidden"]):
                    item = console.database.item_by_id(thisroom["exits"][ex]["key"])
                    console.msg("Unlocked with: {0} ({1})".format(item["name"], item["id"]))
                found_something = True
                break

        # Maybe it's the username of a user.
        user = console.database.user_by_name(' '.join(args).lower())
        if user and console.database.online(user["name"]):
            console.msg("{0} ({1})".format(user["nick"], user["name"]))

            # Description exists, so show it.
            if user["desc"]:
                console.msg(user["desc"])  # Print user description.
            found_something = True

        # Maybe it's the nickname of a user.
        user = console.database.user_by_nick(' '.join(args).lower())
        if user and console.database.online(user["name"]):
            console.msg("{0} ({1})".format(user["nick"], user["name"]))

            # Description exists, so show it.
            if user["desc"]:
                console.msg(user["desc"])  # Print user description.
            found_something = True

        # We didn't find anything by that name.
        if not found_something:
            console.msg("{0}: No such thing: {1}".format(NAME, ' '.join(args)))
            return False

        # Finished.
        return True
