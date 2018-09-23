from datatype import Room, User, Item

USAGE = "rename self <nickname>"
DESCRIPTION = "Set your player nickname."


def COMMAND(console, database, args):
    if len(args) == 0:
        return False

    # Make sure we are logged in.
    if not console.user:
        return False

    console.user.nick = ' '.join(args)
    database.update(console.user)
    return True
