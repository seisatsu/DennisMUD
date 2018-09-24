NAME = "describe self"
USAGE = "describe self <description>"
DESCRIPTION = "Set your player description."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    console.user.desc = ' '.join(args)
    database.update(console.user)
    console.msg(NAME + ": done")
    return True