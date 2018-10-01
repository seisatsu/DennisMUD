NAME = "enable chat"
CATEGORIES = ["messaging", "settings"]
USAGE = "enable chat"
DESCRIPTION = "Participate in and receive messages from the general chat."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Check if chat is already enabled.
    if console.user["chat"]["enabled"]:
        console.msg(NAME + ": chat is already enabled")
        return False

    console.user["chat"]["enabled"] = True
    database.upsert_user(console.user)

    console.msg(NAME + ": done")
    return True
