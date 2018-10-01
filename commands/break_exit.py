NAME = "break exit"
CATEGORIES = ["exits"]
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

    try:
        exitid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Find the current room.
    thisroom = database.room_by_id(console.user["room"])
    if thisroom:
        # Find out if the exit exists in this room.
        if exitid > len(thisroom["exits"])-1 or exitid < 0:
            console.msg(NAME + ": no such exit")
            return False
        if thisroom["locked"] and not console.user["wizard"] and console.user["name"] not in thisroom["owners"]:
            console.msg(NAME + ": the room is locked")
            return False
        if console.user["name"] not in thisroom["exits"][exitid]["owners"] \
                and console.user["name"] not in thisroom["owners"] and not console.user["wizard"]:
            console.msg(NAME + ": you do not own this exit or this room")
            return False
        del thisroom["exits"][exitid]
        database.upsert_room(thisroom)
        console.msg(NAME + ": done")
        return True

    # Couldn't find the current room.
    console.msg("warning: current room does not exist")
    return False
