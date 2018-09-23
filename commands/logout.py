from datatype import Room, User, Item

USAGE = "logout"
DESCRIPTION = "Log out if logged in."


def COMMAND(console, database, args):
        if len(args) != 0:
            return False

        # Look for the current room.
        thisroom = database.filter(Room, {"id": console.user.room})
        if not len(thisroom):
            return False  # The current room does not exist?!
        thisroom = thisroom[0]

        # If we are in the room, take us out.
        if console.user.name in thisroom.users:
            thisroom.users.remove(console.user.name)
            database.update(thisroom)

        # Take us offline
        if console.user.online:
            console.user.online = False
            database.update(console.user)
            console.user = None
            return True
        return False

