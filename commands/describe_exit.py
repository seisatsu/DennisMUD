NAME = "describe exit"
USAGE = "describe exit <id> <description>"
DESCRIPTION = "Set the description of the exit <id> in this room."


def COMMAND(console, database, args):
    if len(args) < 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        exitid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Make the exit is in this room.
    thisroom = database.room_by_id(console.user["room"])
    if thisroom:
        if exitid > len(thisroom["exits"])-1 or exitid < 0:
            console.msg(NAME + ": no such exit")
            return False
        thisroom["exits"][exitid]["desc"] = ' '.join(args[1:])
        database.upsert_room(thisroom)
        console.msg(NAME + ": done")
        return True
    console.msg("warning: current room does not exist")
    return False
