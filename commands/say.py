NAME = "say"
USAGE = "say <message>"
DESCRIPTION = "Send a message to everyone in the same room as you."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    console.broadcast_room("<" + console.user["nick"] + ">: " + ' '.join(args))

    return True