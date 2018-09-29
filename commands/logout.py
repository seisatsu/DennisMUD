NAME = "logout"
USAGE = "logout"
DESCRIPTION = "Log out if logged in."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Not logged in yet.
    if not console.user or not console.user["online"]:
        console.msg(NAME + ": not logged in")
        return False

    # Look for the current room.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    # If we are in the room, take us out.
    if console.user["name"] in thisroom["users"]:
        console.broadcast_room(console.user["nick"] + " left the dream")
        thisroom["users"].remove(console.user["name"])
        database.upsert_room(thisroom)

    # Take us offline
    console.user["online"] = False
    database.upsert_user(console.user)
    console.user = None
    console.msg("logged out")
    return True
