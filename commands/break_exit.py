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
    thisroom = database.room_by_id(console.user["room"])
    if thisroom:
        # Find out if the exit exists in this room.
        if exitid > len(thisroom["exits"])-1 or exitid < 0:
            console.msg(NAME + ": no such exit")
            return False
        del thisroom["exits"][exitid]
        database.upsert_room(thisroom)
        console.msg(NAME + ": done")
        return True

    # Couldn't find the current room.
    console.msg("warning: current room does not exist")
    return False
