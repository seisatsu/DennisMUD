import hashlib
from datatype import Room, User, Item

USAGE = "login <username> <password>"
DESCRIPTION = "Log in as the user <username> if not currently logged in, using <password>."


def COMMAND(console, database, args):
        # args = [username, password]
        if len(args) != 2:
            console.msg(USAGE)
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
        thisroom = database.filter(Room, {"id": console.user.room})
        if not len(thisroom):
            console.msg("warning: current room does not exist")
            return False  # The current room does not exist?!
        thisroom = thisroom[0]

        # If we are not in the room, put us there.
        if not console.user.name in thisroom.users:
            thisroom.users.append(console.user.name)
            database.update(thisroom)

        console.msg("Logged in as \""+console.user.name+"\".")
        return True
