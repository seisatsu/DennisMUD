NAME = "seal inbound"
USAGE = "seal inbound"
DESCRIPTION = "Prevent new exits from being made that lead to the current room."


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

    if r["sealed"]:
        console.msg(NAME + ": this room is already inbound sealed")
        return False
    r["sealed"] = True
    database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
