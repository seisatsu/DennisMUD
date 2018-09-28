NAME = "grant room"
USAGE = "grant room <username>"
DESCRIPTION = "Add user <username> to the owners of the current room."


def COMMAND(console, database, args):
    if len(args) != 1:
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

    u = database.user_by_name(args[0].lower())
    if not u:
        console.msg(NAME + ": no such user")
        return False

    # Check if the named user is already an owner.
    if args[0].lower() in r["owners"]:
        console.msg(NAME + ": user already an owner of this room")

    r["owners"].append(args[0].lower())
    database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
