NAME = "revoke exit"
USAGE = "revoke exit <id> <username>"
DESCRIPTION = "Remove user <username> from the owners of the exit <id> in the current room."


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
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    roomid = console.user["room"]
    r = database.room_by_id(roomid)

    # Make sure we own the exit or the room.
    if console.user["name"] not in r["exits"][exitid]["owners"] \
            and console.user["name"].lower() not in r["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this exit or this room")
        return False

    u = database.user_by_name(args[1].lower())
    if not u:
        console.msg(NAME + ": no such user")
        return False

    # Check if the named user is already an owner.
    if not args[1].lower() in r["exits"][exitid]["owners"]:
        console.msg(NAME + ": user already not an owner of this exit")

    r["exits"][exitid]["owners"].remove(args[1].lower())
    database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
