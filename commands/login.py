import hashlib

NAME = "login"
USAGE = "login <username> <password>"
DESCRIPTION = "Log in as the user <username> if not currently logged in, using <password>."


def COMMAND(console, database, args):
    # args = [username, password]
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    if console.user:
        console.msg(NAME + ": already logged in")
        return False

    thisuser = database.users.find_one(
        {
            "name": args[0],
            "passhash": hashlib.sha256(args[1].encode()).hexdigest()
        }
    )
    if not thisuser:
        console.msg(NAME + ": bad credentials")
        return False  # Bad login.
    console.user = thisuser
    console.user["online"] = True
    database.upsert_user(console.user)

    # Look for the current room.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    # If we are not in the room, put us there.
    if not console.user["name"] in thisroom["users"]:
        thisroom["users"].append(console.user["name"])
        database.upsert_room(thisroom)

    console.msg("logged in as \"" + console.user["name"] + "\"")
    console.broadcast_room(console.user["nick"] + " entered the dream")
    console.command("look", False)
    return True
