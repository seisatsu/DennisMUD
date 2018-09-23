NAME = "make exit"
USAGE = "make exit <destination> <name>"
DESCRIPTION = "Create an exit called <name> in the current room, leading to the room with ID <destination>."


def COMMAND(console, database, args):
    if len(args) < 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    dest = int(args[0])
    name = ' '.join(args[1:])

    # Check if an exit by this name already exists. Case insensitive.
    thisroom = database.room_by_id(console.user.room)
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!
    exits = thisroom["exits"]
    if len(exits):
        for e in exits:
            if e["name"].lower() == name.lower():
                return False  # An exit by this name already exists.

    # Check if the destination room exists.
    destroom = database.room_by_id(dest)
    if not destroom:
        return False  # The destination room does not exist.

    # Create our new exit.
    newexit = {"dest": dest, "name": name, "desc": ""}
    thisroom.exits.append(newexit)

    # Save.
    database.update(thisroom)
    return True
