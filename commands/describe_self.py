from datatype import Room, User, Item

USAGE = "describe self <description>"
DESCRIPTION = "Set your player description."


def COMMAND(console, database, args):
    if len(args) == 0:
        return False

    # Make sure we are logged in.
    if not console.user:
        return False

    console.user.desc = ' '.join(args)
    database.update(console.user)
    return True
