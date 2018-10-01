NAME = "redirect exit"
CATEGORIES = ["exits"]
USAGE = "redirect exit <id> <destination>"
DESCRIPTION = "Set the destination of the exit <id> in this room to <destination>."


def COMMAND(console, database, args):
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        exitid = int(args[0])
        dest = int(args[1])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure the exit is in this room.
    thisroom = database.room_by_id(console.user["room"])
    if thisroom:
        if exitid > len(thisroom["exits"])-1 or exitid < 0:
            console.msg(NAME + ": no such exit")
            return False
        # Check if the destination room exists.
        destroom = database.room_by_id(dest)
        if not destroom:
            console.msg(NAME + ": destination room does not exist")
            return False  # The destination room does not exist.
        if thisroom["locked"] and not console.user["wizard"] and console.user["name"] not in thisroom["owners"]:
            console.msg(NAME + ": the room is locked")
            return False
        thisroom["exits"][exitid]["dest"] = dest
        database.upsert_room(thisroom)
        console.msg(NAME + ": done")
        return True
    console.msg("warning: current room does not exist")
    return False
