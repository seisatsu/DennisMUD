NAME = "rename self"
CATEGORIES = ["settings", "users"]
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

    for u in database.users.find():
        if ' '.join(args).lower() == u["nick"].lower():
            console.msg(NAME + ": that nickname is already in use")
            return False

    console.user["nick"] = ' '.join(args)
    database.upsert_user(console.user)
    console.msg(NAME + ": done")
    return True
