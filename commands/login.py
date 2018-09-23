import hashlib
from datatype import User

NAME = "login"
USAGE = "login <username> <password>"
DESCRIPTION = "Log in as the user <username> if not currently logged in, using <password>."


def COMMAND(console, database, args):
    # args = [username, password]
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    if console.user:
        console.msg("login: already logged in")
        return False

    thisuser = database.filter(
        User, {
            "name": args[0],
            "passhash": hashlib.sha256(args[1].encode()).hexdigest()
        }
    )
    if len(thisuser) == 0:
        console.msg("login: bad credentials")
        return False  # Bad login.
    console.user = thisuser[0]
    console.user.online = True
    database.update(console.user)

    # Look for the current room.
    thisroom = database.room_by_id(console.user.room)
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    # If we are not in the room, put us there.
    if not console.user.name in thisroom.users:
        thisroom.users.append(console.user.name)
        database.update(thisroom)

    console.msg("logged in as \"" + console.user.name + "\".")
    return True
