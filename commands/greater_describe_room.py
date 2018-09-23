from datatype import Room, User, Item

USAGE = "greater describe room <description>"
DESCRIPTION = "Set the description of the room you are in, even if you are not its owner."


def COMMAND(console, database, args):
    if len(args) == 0:
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user or not console.user.wizard:
        return False

    roomid = console.user.room
    r = database.room_by_id(roomid)
    r.desc = ' '.join(args)
    database.update(r)
    return True
