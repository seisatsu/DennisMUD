NAME = "look"
USAGE = "look [name]"
DESCRIPTION = "Look at the current room or the named object."


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
                itemlist.append(itemlookup["name"])
        if itemlist:
            console.msg("Items: " + ", ".join(itemlist))
        exitlist = []
        for e in range(len(thisroom["exits"])):
            exitlist.append(thisroom["exits"][e]["name"])
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
                # Print exit name, ID, and destination.
                console.msg(thisroom["exits"][e]["name"] + " (" + str(e) + ") -> " + str(thisroom["exits"][e]["dest"]))
                if thisroom["exits"][e]["desc"]:
                    console.msg(thisroom["exits"][e]["desc"])  # Print exit description.
                found_something = True
                break

        # Might be the username of a user.
        u = database.user_by_name(' '.join(args).lower())
        if u:
            console.msg(u["nick"] + " (" + u["name"] + ")")  # Print user nickname and real name.
            if u["desc"]:
                console.msg(u["desc"])  # Print user description.
            found_something = True

        # Might be the nickname of a user.
        u = database.user_by_nick(' '.join(args).lower())
        if u:
            console.msg(u["nick"] + " (" + u["name"] + ")")  # Print user nickname and real name.
            if u["desc"]:
                console.msg(u["desc"])  # Print user description.
            found_something = True

        if found_something:
            return True
        console.msg(NAME + ": no such thing")
        return False
