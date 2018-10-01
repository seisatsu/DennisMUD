NAME = "chat"
CATEGORIES = ["messaging"]
USAGE = "chat <message>"
DESCRIPTION = "Send a message to the general chat."


def COMMAND(console, database, args):
    if len(args) < 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Make sure chat is enabled.
    if not console.user["chat"]["enabled"]:
        console.msg(NAME + ": enable chat first")
        return False

    for u in console.router.users:
        if console.router.users[u].user and console.router.users[u].user["chat"]["enabled"]:
            if not console.user["name"] in console.router.users[u].user["chat"]["ignored"]:
                console.router.users[u].msg("# <" + console.user["name"] + ">: " + ' '.join(args))

    return True
