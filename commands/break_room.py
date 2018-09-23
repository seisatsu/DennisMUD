NAME = "break room"
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

    roomid = int(args[0])

    # Check if the room exists.
    r = database.room_by_id(roomid)
    if r:
        # Check that we own the room.
        if r.owner == console.user.name:
            # Delete the room.
            database.delete(r)

            console.log("break room", "success", "destroyed room", str(roomid))
            return True

        # We don't own this room.
        console.log("break room", "failure", "not the owner of room", str(roomid))
        return False

    # No room with that ID exists.
    console.log("break room", "failure", "no such room", str(roomid))
    return False
