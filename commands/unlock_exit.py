NAME = "unlock exit"
CATEGORIES = ["exits"]
USAGE = "unlock exit <id>"
DESCRIPTION = "Allows anyone to use the exit <id> in this room."


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

    roomid = console.user["room"]
    r = database.room_by_id(roomid)

    # Make sure the exit exists.
    if exitid > len(r["exits"]) - 1 or exitid < 0:
        console.msg(NAME + ": no such exit")
        return False

    # Make sure we own the exit or the room.
    if console.user["name"] not in r["exits"][exitid]["owners"] \
            and console.user["name"] not in r["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this exit or this room")
        return False

    if not r["exits"][exitid]["locked"]:
        console.msg(NAME + ": this exit is already unlocked")
        return False
    r["exits"][exitid]["locked"] = False
    database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
