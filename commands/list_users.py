NAME = "list users"
USAGE = "list users"
DESCRIPTION = "List all online users in the world."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    users = database.users.find().sort("name", 1)
    if users.count():
        for u in users:
            if u["online"]:
                console.msg(u["name"] + ": " + u["nick"])
        if console.user["wizard"]:
            for u in users:
                if u["offline"]:
                    console.msg(u["name"] + ": " + u["nick"] + " (offline)")
    else:
        console.msg(NAME + ": no users?!")

    return True
