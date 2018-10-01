NAME = "lookup room"
CATEGORIES = ["rooms"]
USAGE = "lookup room <name>"
DESCRIPTION = "Find the ID of the room <name>."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    rooms = database.rooms.find()
    for r in rooms:
        if r["name"].lower() == ' '.join(args).lower():
            console.msg(r["name"] + ": " + str(r["id"]))
            return True

    # Couldn't find the room.
    console.msg(NAME + ": no such room")
    return False
