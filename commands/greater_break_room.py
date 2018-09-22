from datatype import Room, User, Item

USAGE = "greater break room <room>"
DESCRIPTION = "Break the room with ID <room> even if you aren't its owner."

def COMMAND(console, database, args=[]):
        if len(args) != 1:
            return False
        
        roomid = int(args[0])
            
        # Make sure we are logged in, and a wizard.
        if not console.user or not console.user.wizard:
            return False
        
        # Check if the room exists.
        r = database.filter(Room, {"id": roomid})
        if len(r):
            r = r[0]
            # Delete the room.
            database.delete(r)
            return True
            
        # No room with that ID exists, or we do not own it.
        return False

