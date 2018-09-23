from datatype import Room, User, Item

USAGE = "logout"
DESCRIPTION = "Log out if logged in."


def COMMAND(console, database, args):
        if len(args) != 0:
            return False
        
        if console.user.online:
            console.user.online = False
            database.update(console.user)
            console.user = None
            return True
        return False

