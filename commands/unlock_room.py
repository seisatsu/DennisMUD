NAME = "unlock room"
USAGE = "unlock room"
DESCRIPTION = "Allow exits to be added, removed, or modified in this room."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    roomid = console.user["room"]
    r = database.room_by_id(roomid)

    # Make sure we are the room's owner.
    if console.user["name"] not in r["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this room")
        return False

    if not r["locked"]:
        console.msg(NAME + ": this room is already unlocked")
        return False
    r["locked"] = False
    database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
