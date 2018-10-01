NAME = "break room"
CATEGORIES = ["rooms"]
USAGE = "break room <room>"
DESCRIPTION = "Break the room with ID <room> if you are its owner."


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        roomid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Check if the room exists.
    r = database.room_by_id(roomid)
    if r:
        # Check that we own the room.
        if console.user["name"] in r["owners"] or console.user["wizard"]:
            # Make sure the room is empty.
            if r["users"]:
                console.msg(NAME + ": you cannot break an occupied room")
                return False

            # Delete the room.
            database.delete_room(r)

            console.msg(NAME + ": done")
            return True

        # We don't own this room.
        console.msg(NAME + ": you do not own this room")
        return False

    # No room with that ID exists.
    console.msg(NAME + ": no such room")
    return False
