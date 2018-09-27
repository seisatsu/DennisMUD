NAME = "list users"
USAGE = "list users"
DESCRIPTION = "List all users in the world."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False
    if not console.user["wizard"]:
        console.msg(NAME + ": you do not have permission to use this command")
        return False

    users = database.users.find().sort("name", 1)
    if users.count():
        for u in users:
            console.msg(u["name"] + ": " + u["nick"])
    else:
        console.msg(NAME + ": no users?!")

    return True
