NAME = "make room"
CATEGORIES = ["rooms"]
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
    rooms = list(database.rooms.find().sort("id", -1))
    if rooms:
        for r in rooms:
            if r["name"].lower() == name.lower():
                console.msg(NAME + ": a room by this name already exists")
                return False  # A room by this name already exists.

    # Find the highest numbered currently existing room ID.
    if rooms:
        lastroom = rooms[0]["id"]
    else:
        lastroom = -1

    # Create our new room with an ID one higher.
    newroom = {
        "owners": [console.user["name"]],
        "id": lastroom + 1,
        "name": name,
        "desc": "",
        "users": [],
        "exits": [],
        "items": [],
        "keys": [],
        "locked": False,
        "sealed": False
    }

    # Save.
    database.upsert_room(newroom)
    console.msg(NAME + ": done (id: " + str(newroom["id"]) + ")")
    return True
