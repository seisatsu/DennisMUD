from datatype import User

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
    if not console.user.wizard:
        console.msg(NAME + ": you do not have permission to use this command")
        return False

    users = database.filter(User, {}).sort("name")
    if len(users):
        for u in users:
            print(u.name + ": " + u.nick)
