from datatype import Room, User, Item

USAGE = "look [name]"
DESCRIPTION = "Look at the current room or the named object."


def COMMAND(console, database, args):
    # Make sure we are logged in.
    if not console.user:
        return False

    # Get the current room.
    thisroom = database.filter(Room, {"id": console.user.room})
    if not len(thisroom):
        return False
    thisroom = thisroom[0]

    if len(args) == 0:
        # Look at the current room.
        # TODO: Enumerate occupants, exits, and items.
        print(str(thisroom.id)+": "+thisroom.name)
        print("Owned by: "+thisroom.owner)
        print(thisroom.desc)
        print("Occupants: "+", ".join(thisroom.users))
        itemlist = []
        for i in thisroom["items"]:
            itemlookup = database.item_by_id(i)
            if itemlookup:
                itemlist.append(itemlookup["name"])
        print("Items: " + ", ".join(itemlist))
        exitlist = []
        for e in thisroom.exits:
            exitlist.append(e["name"])
        print("Exits: " + ", ".join(exitlist))
        return True

    else:
        found_something = False

        if len(args) == 1:
            # Might be the name of a user.
            if args[0].lower() == "self":
                # Looking at ourselves.
                print(console.user.nick + " (" + console.user.name + ")")  # Print user nickname and real name.
                print(console.user.desc)  # Print user description.
                return True

            for uname in thisroom.users:
                if uname.lower() == args.lower():
                    # We are looking at this user.
                    u = database.user_by_name(uname)
                    print(u.nick+" ("+u.name+")")  # Print user nickname and real name.
                    print(u.desc)  # Print user description.
                    found_something = True
                    break

        # Might be an item in the room.
        for itemid in thisroom["items"]:  # Oops, "items" mirrors a method of lists.
            i = database.item_by_id(itemid)
            if i.name.lower() == ' '.join(args).lower():
                print(str(i.id)+": "+i.name)  # Print item ID and name.
                print(i.desc)  # Print item description.
                found_something = True
                break

        # Might be an item in your inventory.
        for itemid in console.user.inventory:
            i = database.item_by_id(itemid)
            if i.name.lower() == ' '.join(args).lower():
                print(str(i.id)+": "+i.name)  # Print item ID and name.
                print(i.desc)  # Print item description.
                found_something = True
                break

        # Might be an exit in the room.
        for e in thisroom.exits:
            if e["name"].lower() == ' '.join(args).lower():
                print(e["name"]+" -> "+e["dest"])  # Print exit name and destination.
                print(e["desc"])  # Print exit description.
                found_something = True
                break

        if found_something:
            return True
        return False
