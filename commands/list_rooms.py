NAME = "list rooms"
USAGE = "list rooms"
DESCRIPTION = "List all rooms in the world."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False
    if not console.user["wizard"]:
        console.msg(NAME + ": you do not have permission to use this command")
        return False

    rooms = database.rooms.find().sort("id", 1)
    if rooms.count():
        for r in rooms:
            console.msg(str(r["id"]) + ": " + r["name"])
    else:
        console.msg(NAME + ": no users")

    return True
