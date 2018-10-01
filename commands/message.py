NAME = "message"
CATEGORIES = ["messaging"]
USAGE = "message <username> <message>"
DESCRIPTION = "Send a message to the user <username>. Does not use nicknames."


def COMMAND(console, database, args):
    if len(args) < 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    for u in console.router.users:
        if console.router.users[u].user and console.router.users[u].user["name"] == args[0].lower():
            if not console.user["name"] in console.router.users[u].user["chat"]["ignored"] or console.user["wizard"]:
                console.router.users[u].msg("<<" + console.user["name"] + ">>: " + ' '.join(args[1:]))
                console.msg("<<" + console.user["name"] + ">>: " + ' '.join(args[1:]))
            return True

    console.msg(NAME + ": no such user is logged in")
    return False
