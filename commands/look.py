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
ALIASES = ["look at", "l", "examine", "x"]
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
            else:
                console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                                  item=itemid)
                console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
        if itemlist:
            console.msg("Items: {0}".format(", ".join(itemlist)))

        # Build and show the exit list.
        exitlist = []
        for ex in range(len(thisroom["exits"])):
            exitlist.append("{0} ({1})".format(thisroom["exits"][ex]["name"], ex))
        if exitlist:
            console.msg("Exits: {0}".format(", ".join(exitlist)))
        else:
            console.msg("No exits in this room. Make one or use `xyzzy` to return to the first room.")
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
        partials = []

        # Save a bit of line space.
        target = ' '.join(args).lower()
        if target == "the":
            console.msg("{0}: Very funny.".format(NAME))
            return False

        # Looking at ourselves. Show user nickname real name, and description.
        if target == "self":
            console.msg("{0} ({1})".format(console.user["nick"], console.user["name"]))

            # Description exists, so show it.
            if console.user["desc"]:
                console.msg(console.user["desc"])

            # If we are sitting or laying down, format a message saying so after the description.
            if console.user["pronouns"] == "female":
                if console["posture"] and console["posture_item"]:
                    console.msg("\nShe is {0} on {1}.".format(console["posture"],
                                                              COMMON.format_item(NAME, console["posture_item"])))
                elif console["posture"]:
                    console.msg("\nShe is {0}.".format(console["posture"]))
                return True
            elif console.user["pronouns"] == "male":
                if console["posture"] and console["posture_item"]:
                    console.msg("\nHe is {0} on {1}.".format(console["posture"],
                                                             COMMON.format_item(NAME, console["posture_item"])))
                elif console["posture"]:
                    console.msg("\nHe is {0}.".format(console["posture"]))
                return True
            else:
                if console["posture"] and console["posture_item"]:
                    console.msg("\nThey are {0} on {1}.".format(console["posture"],
                                                                COMMON.format_item(NAME, console["posture_item"])))
                elif console["posture"]:
                    console.msg("\nThey are {0}.".format(console["posture"]))
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

            # Record partial matches.
            if target in item["name"].lower() or target.replace("the ", "", 1) in item["name"].lower():
                partials.append(item["name"].lower())

            # It was an item in the room. Show the item's name, ID, owners, description, and attributes.
            if target in [item["name"].lower(), "the " + item["name"].lower()]:
                # Only enumerate item attributes if we are the item owner or a wizard.
                if console.user["name"] in item["owners"] or console.user["wizard"]:
                    if item["duplified"]:
                        attributes.append("[duplified]")
                    if item["glued"]:
                        attributes.append("[glued]")
                    if item["telekey"] is not None:
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

            # Record partial matches.
            if target in item["name"].lower() or target.replace("the ", "", 1) in item["name"].lower():
                partials.append(item["name"].lower())

            # It was an item in our inventory. Show the item's name, ID, owners, description, and attributes,
            # but only if we didn't already see it in the current room. Also check if the user prepended "the ".
            if target in [item["name"].lower(), "the " + item["name"].lower()] and item["id"] != found_item:
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
            # Record partial matches.
            if target in thisroom["exits"][ex]["name"].lower() or \
                    target.replace("the ", "", 1) in thisroom["exits"][ex]["name"].lower():
                partials.append(thisroom["exits"][ex]["name"].lower())

            # It was an exit in the current room. Show the exit name, destination,
            # description, ID, owners, and any key information.
            if target in [thisroom["exits"][ex]["name"].lower(), "the " + thisroom["exits"][ex]["name"].lower()]:
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
        # Record partial matches.
        for username in thisroom["users"]:
            if target in username:
                partials.append(username)

        # Look for an exact username match.
        user = console.database.user_by_name(target)
        if user and console.database.online(user["name"]) and user["name"] in thisroom["users"]:
            console.msg("{0} ({1})".format(user["nick"], user["name"]))

            # Description exists, so show it.
            if user["desc"]:
                console.msg(user["desc"])  # Print user description.

            # If they are sitting or laying down, format a message saying so after the description.
            userconsole = console.shell.console_by_username(user["name"])
            if console.user["pronouns"] == "female":
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\nShe is {0} on {1}.".format(userconsole["posture"],
                                                              COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\nShe is {0}.".format(userconsole["posture"]))
            elif console.user["pronouns"] == "male":
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\nHe is {0} on {1}.".format(userconsole["posture"],
                                                             COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\nHe is {0}.".format(userconsole["posture"]))
            else:
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\nThey are {0} on {1}.".format(userconsole["posture"],
                                                                COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\nThey are {0}.".format(userconsole["posture"]))
            found_something = True

        # Maybe it's the nickname of a user.
        # Record partial matches.
        for username in thisroom["users"]:
            usertemp = console.database.user_by_nick(username)
            if usertemp:
                if target in usertemp["nick"]:
                    partials.append(usertemp["nick"])

        # Look for an exact nickname match.
        user = console.database.user_by_nick(target)
        if user and console.database.online(user["name"]):
            console.msg("{0} ({1})".format(user["nick"], user["name"]))

            # Description exists, so show it.
            if user["desc"]:
                console.msg(user["desc"])  # Print user description.

            # If they are sitting or laying down, format a message saying so after the description.
            userconsole = console.shell.console_by_username(user["name"])
            if console.user["pronouns"] == "female":
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\nShe is {0} on {1}.".format(userconsole["posture"],
                                                              COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\nShe is {0}.".format(userconsole["posture"]))
            elif console.user["pronouns"] == "male":
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\nHe is {0} on {1}.".format(userconsole["posture"],
                                                             COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\nHe is {0}.".format(userconsole["posture"]))
            else:
                if userconsole["posture"] and userconsole["posture_item"]:
                    console.msg("\nThey are {0} on {1}.".format(userconsole["posture"],
                                                                COMMON.format_item(NAME, userconsole["posture_item"])))
                elif userconsole["posture"]:
                    console.msg("\nThey are {0}.".format(userconsole["posture"]))
            found_something = True

        # We didn't find anything by that name. See if we found partial matches.
        if not found_something:
            # Eliminate duplicate matches.
            if partials:
                partials = list(dict.fromkeys(partials))

            # We got exactly one partial match. Assume that one.
            if len(partials) == 1:
                return COMMAND(console, partials[0].split(' '))

            # We got up to 5 partial matches. List them.
            elif partials and len(partials) <= 5:
                console.msg("{0}: Did you mean one of: {1}".format(NAME, ', '.join(partials)))
                return False

            # We got too many matches.
            elif len(partials) > 5:
                console.msg("{0}: Too many possible matches.".format(NAME))
                return False

            # Really nothing.
            else:
                console.msg("{0}: No such thing: {1}".format(NAME, ' '.join(args)))
            return False

        # Finished.
        return True
