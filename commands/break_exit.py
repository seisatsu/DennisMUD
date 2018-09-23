NAME = "break exit"
USAGE = "break exit <name>"
DESCRIPTION = "Break the exit called <name> in the current room."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    name = ' '.join(args)

    # Find the current room.
    thisroom = database.room_by_id(console.user.room)
    if len(thisroom):
        # Find the exit if it exists in this room.
        for e in range(len(thisroom.exits)):
            if thisroom.exits[e]["name"].lower() == name.lower():
                # Delete the exit.
                del thisroom.exits[e]
                database.update(thisroom)
                return True

    # Couldn't find the current room, or the exit does not exist there.
    return False
