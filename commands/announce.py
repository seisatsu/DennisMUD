NAME = "announce"
USAGE = "announce <message>"
DESCRIPTION = "(WIZARDS ONLY) Send a message to all users."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False
    if not console.user["wizard"]:
        console.msg(NAME + ": you do not have permission to use this command")
        return False

    console.broadcast("<<<" + console.user["nick"] + ">>>: " + ' '.join(args))

    return True