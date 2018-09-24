NAME = "look"
USAGE = "look [name]"
DESCRIPTION = "Look at the current room or the named object."


def COMMAND(console, database, args):
    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Look for the current room.
    thisroom = database.room_by_id(console.user.room)
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    if len(args) == 0:
        # Look at the current room.
        console.msg(thisroom.name + " (" + str(thisroom.id) + ")")
        console.msg("Owned by: " + thisroom.owner)
        if thisroom.desc:
            console.msg(thisroom.desc)
        console.msg("Occupants: " + ", ".join(thisroom.users))
        itemlist = []
        for i in thisroom["items"]:
            itemlookup = database.item_by_id(i)
            if itemlookup:
                itemlist.append(itemlookup["name"])
        if itemlist:
            console.msg("Items: " + ", ".join(itemlist))
        exitlist = []
        for e in thisroom.exits:
            exitlist.append(e["name"])
        if exitlist:
            console.msg("Exits: " + ", ".join(exitlist))
        return True

    else:
        found_something = False

        if len(args) == 1:
            # Might be the name of a user.
            if args[0].lower() == "self":
                # Looking at ourselves.
                console.msg(console.user.nick + " (" + console.user.name + ")")  # Print user nickname and real name.
                if console.user.desc:
                    console.msg(console.user.desc)  # Print user description.
                return True

            for uname in thisroom.users:
                if uname.lower() == args[0].lower():
                    # We are looking at this user.
                    u = database.user_by_name(uname)
                    console.msg(u.nick + " (" + u.name + ")")  # Print user nickname and real name.
                    if u.desc:
                        console.msg(u.desc)  # Print user description.
                    found_something = True
                    break

        # Might be an item in the room.
        for itemid in thisroom["items"]:  # Oops, "items" mirrors a method of lists.
            i = database.item_by_id(itemid)
            if i.name.lower() == ' '.join(args).lower():
                console.msg(str(i.id) + ": " + i.name)  # Print item ID and name.
                if i.desc:
                    console.msg(i.desc)  # Print item description.
                found_something = True
                break

        # Might be an item in your inventory.
        for itemid in console.user.inventory:
            i = database.item_by_id(itemid)
            if i.name.lower() == ' '.join(args).lower():
                console.msg(str(i.id) + ": " + i.name)  # Print item ID and name.
                if i.desc:
                    console.msg(i.desc)  # Print item description.
                found_something = True
                break

        # Might be an exit in the room.
        for e in thisroom.exits:
            if e["name"].lower() == ' '.join(args).lower():
                console.msg(e["name"] + " -> " + e["dest"])  # Print exit name and destination.
                if e["desc"]:
                    console.msg(e["desc"])  # Print exit description.
                found_something = True
                break

        # Might be the nickname of a user.
        for uname in thisroom.users:
            u = database.user_by_name(uname)
            if u.nick.lower() == args[0].lower():
                console.msg(u.nick + " (" + u.name + ")")  # Print user nickname and real name.
                if u.desc:
                    console.msg(u.desc)  # Print user description.
                found_something = True
                break

        if found_something:
            return True
        console.msg(NAME + ": no such thing")
        return False
