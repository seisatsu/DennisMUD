NAME = "realname"
CATEGORIES = ["users"]
USAGE = "realname <nickname>"
DESCRIPTION = "Find the real username of the user <nickname>."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    u = database.user_by_nick(' '.join(args).lower())
    if u:
        console.msg(u["nick"] + ": " + u["name"])
        return True

    # Couldn't find the user.
    console.msg(NAME + ": no such user")
    return False
