NAME = "logout"
USAGE = "logout"
DESCRIPTION = "Log out if logged in."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Look for the current room.
    thisroom = database.room_by_id(console.user.room)
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    # If we are in the room, take us out.
    if console.user.name in thisroom.users:
        thisroom.users.remove(console.user.name)
        database.update(thisroom)

    # Take us offline
    if console.user.online:
        console.user.online = False
        database.update(console.user)
        console.user = None
        console.msg("logged out")
        return True
    console.msg(NAME + ": not logged in")
    return False
