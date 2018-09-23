NAME = "greater break room"
USAGE = "greater break room <room>"
DESCRIPTION = "Break the room with ID <room> even if you aren't its owner."


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False
    if not console.user.wizard:
        console.msg(NAME + ": you do not have permission to use this command")
        return False

    roomid = int(args[0])

    # Check if the room exists.
    r = database.room_by_id(roomid)
    if r:
        # Delete the room.
        database.delete(r)
        return True

    # No room with that ID exists, or we do not own it.
    return False
