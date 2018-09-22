from datatype import Room, User, Item

USAGE = "break room <room>"
DESCRIPTION = "Break the room with ID <room> if you are its owner."

def COMMAND(console, database, args=[]):
        if len(args) != 1:
            return False
        
        roomid = int(args[0])
            
        # Make sure we are logged in.
        if not console.user:
            return False
        
        # Check if the room exists.
        r = database.filter(Room, {"id": roomid})
        if len(r):
            r = r[0]
            # Check that we own the room.
            if r.owner == console.user.name:
                # Delete the room.
                database.delete(r)
                
                return True
            
        # No room with that ID exists, or we do not own it.
        return False

