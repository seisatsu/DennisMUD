NAME = "unignore user"
CATEGORIES = ["messaging", "settings", "users"]
USAGE = "unignore user <username>"
DESCRIPTION = "Unignore general chat messages and private messages from the user <username>."


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

    # Check if user is already not ignored.
    if targetuser["name"] not in console.user["chat"]["ignored"]:
        console.msg(NAME + ": already not ignoring user")
        return False

    console.user["chat"]["ignored"].remove(targetuser["name"])
    database.upsert_user(console.user)

    console.msg(NAME + ": done")
    return True
