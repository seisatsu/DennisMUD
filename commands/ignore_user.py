NAME = "ignore user"
CATEGORIES = ["messaging", "settings", "users"]
USAGE = "ignore user <username>"
DESCRIPTION = "Ignore general chat messages and private messages from the user <username>."


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Lookup user.
    targetuser = database.user_by_name(args[0])
    if not targetuser:
        # No such user.
        console.msg(NAME + ": no such user")
        return False

    # Check if user is already ignored.
    if targetuser["name"] in console.user["chat"]["ignored"]:
        console.msg(NAME + ": already ignoring user")
        return False

    console.user["chat"]["ignored"].append(targetuser["name"])
    database.upsert_user(console.user)

    console.msg(NAME + ": done")
    return True
