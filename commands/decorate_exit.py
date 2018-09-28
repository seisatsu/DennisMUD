NAME = "decorate exit"
USAGE = "decorate exit <id> <action>"
DESCRIPTION = "Set a custom <action> to display after the player's name when they use the exit <id>."


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

    # Make sure the exit is in this room.
    thisroom = database.room_by_id(console.user["room"])
    if thisroom:
        if exitid > len(thisroom["exits"])-1 or exitid < 0:
            console.msg(NAME + ": no such exit")
            return False
        if thisroom["locked"] and not console.user["wizard"] and console.user["name"].lower() not in thisroom["owners"]:
            console.msg(NAME + ": the room is locked")
            return False
        thisroom["exits"][exitid]["action"] = ' '.join(args[1:])
        database.upsert_room(thisroom)
        console.msg(NAME + ": done")
        return True
    console.msg("warning: current room does not exist")
    return False
