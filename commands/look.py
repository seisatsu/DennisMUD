#####################
# Dennis MUD        #
# lock.py           #
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

NAME = "look"
CATEGORIES = ["exploration"]
USAGE = "look [name]"
DESCRIPTION = "Look at the current room or the named object or user."


def COMMAND(console, database, args):
    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Look for the current room.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    if len(args) == 0:
        # Look at the current room.
        console.msg(thisroom["name"] + " (" + str(thisroom["id"]) + ")")
        console.msg("Owned by: " + ', '.join(thisroom["owners"]))
        if thisroom["desc"]:
            console.msg(thisroom["desc"])
        userlist = []
        for u in thisroom["users"]:
            userlist.append(database.user_by_name(u)["nick"])
        console.msg("Occupants: " + ", ".join(userlist))
        itemlist = []
        for i in thisroom["items"]:
            itemlookup = database.item_by_id(i)
            if itemlookup:
                itemlist.append(itemlookup["name"] + " (" + str(itemlookup["id"]) + ")")
        if itemlist:
            console.msg("Items: " + ", ".join(itemlist))
        exitlist = []
        for e in range(len(thisroom["exits"])):
            exitlist.append(thisroom["exits"][e]["name"] + " (" + str(e) + ")")
        if exitlist:
            console.msg("Exits: " + ", ".join(exitlist))
        return True

    else:
        found_something = False

        if len(args) == 1 and args[0].lower() == "self":
                # Looking at ourselves. Print user nickname and real name.
                console.msg(console.user["nick"] + " (" + console.user["name"] + ")")
                if console.user["desc"]:
                    console.msg(console.user["desc"])  # Print user description.
                return True

        # Might be an item in the room.
        for itemid in thisroom["items"]:  # Oops, "items" mirrors a method of lists.
            i = database.item_by_id(itemid)
            if i["name"].lower() == ' '.join(args).lower():
                console.msg(i["name"] + " (" + str(i["id"]) + ")")  # Print item ID and name.
                console.msg("Owned by: " + ', '.join(i["owners"]))
                if i["desc"]:
                    console.msg(i["desc"])  # Print item description.
                found_something = True
                break

        # Might be an item in your inventory.
        for itemid in console.user["inventory"]:
            i = database.item_by_id(itemid)
            if i["name"].lower() == ' '.join(args).lower():
                console.msg(i["name"] + " (" + str(i["id"]) + ")")  # Print item ID and name.
                console.msg("Owned by: " + ', '.join(i["owners"]))
                if i["desc"]:
                    console.msg(i["desc"])  # Print item description.
                found_something = True
                break

        # Might be an exit in the room.
        for e in range(len(thisroom["exits"])):
            if thisroom["exits"][e]["name"].lower() == ' '.join(args).lower():
                # Print exit name, ID, destination, and any key information.
                console.msg(thisroom["exits"][e]["name"] + " (" + str(e) + ") -> " + str(thisroom["exits"][e]["dest"]))
                console.msg("Owned by: " + ', '.join(thisroom["exits"][e]["owners"]))
                if thisroom["exits"][e]["desc"]:
                    console.msg(thisroom["exits"][e]["desc"])  # Print exit description.
                if thisroom["exits"][e]["key"]:
                    i = database.item_by_id(thisroom["exits"][e]["key"])
                    console.msg("Unlocked with: " + i["name"] + " (" + str(i["id"]) + ")")  # Print key information.
                found_something = True
                break

        # Might be the username of a user.
        u = database.user_by_name(' '.join(args).lower())
        if u and u["online"]:
            console.msg(u["nick"] + " (" + u["name"] + ")")  # Print user nickname and real name.
            if u["desc"]:
                console.msg(u["desc"])  # Print user description.
            found_something = True

        # Might be the nickname of a user.
        u = database.user_by_nick(' '.join(args).lower())
        if u and u["online"]:
            console.msg(u["nick"] + " (" + u["name"] + ")")  # Print user nickname and real name.
            if u["desc"]:
                console.msg(u["desc"])  # Print user description.
            found_something = True

        if found_something:
            return True
        console.msg(NAME + ": no such thing")
        return False
