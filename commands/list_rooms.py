NAME = "list rooms"
USAGE = "list rooms"
DESCRIPTION = "List all rooms in the world that you own."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    rooms = database.rooms.find().sort("id", 1)
    if rooms.count():
        for r in rooms:
            if console.user["name"] in r["owners"] or console.user["wizard"]:
                # We either own this room, or we are a wizard.
                console.msg(str(r["id"]) + ": " + r["name"])
    else:
        console.msg(NAME + ": no users")

    return True
