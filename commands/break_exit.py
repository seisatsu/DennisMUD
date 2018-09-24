NAME = "break exit"
USAGE = "break exit <exit>"
DESCRIPTION = "Break the exit with ID <exit> in the current room."


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    exitid = int(args[0])

    # Find the current room.
    thisroom = database.room_by_id(console.user.room)
    if thisroom:
        # Find out if the exit exists in this room.
        if exitid > len(thisroom.exits) or exitid < 1:
            console.msg(NAME + ": no such exit")
            return False
        del thisroom.exits[exitid-1]
        database.update(thisroom)
        console.msg(NAME + ": done")
        return True

    # Couldn't find the current room, or the exit does not exist there.
    console.msg(NAME + ": no such exit")
    return False
