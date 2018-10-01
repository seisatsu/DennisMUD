NAME = "revoke room"
CATEGORIES = ["rooms"]
USAGE = "revoke room <username>"
DESCRIPTION = "Remove user <username> from the owners of the current room."


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
    if console.user["name"] not in r["owners"]:
        console.msg(NAME + ": you do not own this room")
        return False

    # Check if the user exists.
    u = database.user_by_name(args[0].lower())
    if not u:
        console.msg(NAME + ": no such user")
        return False

    # Check if the named user is an owner.
    if not args[0].lower() in r["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": user already not an owner of this room")

    r["owners"].remove(args[0].lower())
    database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
