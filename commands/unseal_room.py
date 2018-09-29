NAME = "unseal room"
USAGE = "unseal room"
DESCRIPTION = "Allow new exits to be made that lead to this room."


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

    if not r["sealed"]:
        console.msg(NAME + ": this room is already unsealed")
        return False
    r["sealed"] = False
    database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
