from datatype import Room, User, Item

USAGE = "greater rename room <name>"
DESCRIPTION = "Set the name of the room you are in, even if you are not its owner."


def COMMAND(console, database, args):
    if len(args) == 0:
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user or not console.user.wizard:
        return False

    roomid = console.user.room
    r = database.room_by_id(roomid)
    r.name = ' '.join(args)
    database.update(r)
    return True
