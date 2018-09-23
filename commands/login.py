import hashlib
from datatype import Room, User, Item

USAGE = "login <username> <password>"
DESCRIPTION = "Log in as the user <username> if not currently logged in, using <password>."


def COMMAND(console, database, args):
        # args = [username, password]
        if len(args) != 2:
            return False
            
        if console.user:
            return False

        thisuser = database.filter(
            User, {
                "name": args[0],
                "passhash": hashlib.sha256(args[1].encode()).hexdigest()
            }
        )
        if len(thisuser) == 0:
            return False # Bad login.
        console.user = thisuser[0]
        console.user.online = True
        database.update(console.user)
        return True

