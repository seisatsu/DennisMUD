NAME = "nickname"
USAGE = "nickname <username>"
DESCRIPTION = "Find the nickname of the user <username>."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    u = database.user_by_name(' '.join(args).lower())
    if u:
        console.msg(u["name"] + ": " + u["nick"])
        return True

    # Couldn't find the user.
    console.msg(NAME + ": no such user")
    return False
