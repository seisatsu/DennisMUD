NAME = "greater describe room"
USAGE = "greater describe room <description>"
DESCRIPTION = "Set the description of the room you are in, even if you are not its owner."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False
    if not console.user.wizard:
        console.msg(NAME + ": you do not have permission to use this command")
        return False

    roomid = console.user.room
    r = database.room_by_id(roomid)
    r.desc = ' '.join(args)
    database.update(r)
    console.msg(NAME + ": done")
    return True
