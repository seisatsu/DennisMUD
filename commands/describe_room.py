NAME = "describe room"
USAGE = "describe room <description>"
DESCRIPTION = "Set the description of the room you are in."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    roomid = console.user["room"]
    r = database.room_by_id(roomid)

    # Make sure we are the room's owner.
    if r["owner"].lower() != console.user["name"].lower():
        console.msg(NAME + ": you do not own this room")
        return False

    r["desc"] = ' '.join(args)
    database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
