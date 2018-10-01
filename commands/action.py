NAME = "action"
CATEGORIES = ["messaging"]
USAGE = "action <message>"
DESCRIPTION = "Send a message styled as performing an action."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    console.broadcast_room(console.user["nick"] + " " + ' '.join(args))

    return True
