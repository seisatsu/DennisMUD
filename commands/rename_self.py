NAME = "rename self"
USAGE = "rename self <nickname>"
DESCRIPTION = "Set your player nickname."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    console.user.nick = ' '.join(args)
    database.update(console.user)
    return True
