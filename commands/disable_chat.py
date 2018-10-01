NAME = "disable chat"
CATEGORIES = ["messaging", "settings"]
USAGE = "disable chat"
DESCRIPTION = "Do not participate in and receive messages from the general chat."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Check if chat is already enabled.
    if not console.user["chat"]["enabled"]:
        console.msg(NAME + ": chat is already disabled")
        return False

    console.user["chat"]["enabled"] = False
    database.upsert_user(console.user)

    console.msg(NAME + ": done")
    return True
