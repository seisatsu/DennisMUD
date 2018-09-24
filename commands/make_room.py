from datatype import Room

NAME = "make room"
USAGE = "make room <name>"
DESCRIPTION = "Create a new room called <name>."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    name = ' '.join(args)

    # Check if a room by this name already exists. Case insensitive.
    rooms = database.filter(Room, {})
    if len(rooms):
        for r in rooms:
            if r["name"].lower() == name.lower():
                console.msg(NAME + ": a room by this name already exists")
                return False  # A room by this name already exists.

    # Find the highest numbered currently existing room ID.
    if len(rooms):
        lastroom = rooms.sort("id")[-1]["id"]
    else:
        lastroom = -1

    # Create our new room with an ID one higher.
    newroom = Room({
        "owner": console.user.name,
        "id": lastroom + 1,
        "name": name,
        "desc": "",
        "users": [],
        "exits": [],
        "items": []
    })

    # Save.
    database.insert(newroom)
    console.msg(NAME + ": done (id: " + str(newroom.id) + ")")
    return True
