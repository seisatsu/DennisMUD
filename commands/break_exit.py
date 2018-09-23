from datatype import Room, User, Item

USAGE = "break exit <name>"
DESCRIPTION = "Break the exit called <name> in the current room."


def COMMAND(console, database, args):
        if len(args) == 0:
            return False
        
        name = ' '.join(args)
            
        # Make sure we are logged in.
        if not console.user:
            return False
        
        # Find the current room.
        rooms = database.filter(Room, {id: console.user.room})
        if len(rooms):
            thisroom = room[0]
            # Find the exit if it exists in this room.
            for e in range(len(thisroom.exits)):
                if thisroom.exits[e]["name"].lower() == name.lower():
                    # Delete the exit.
                    del thisroom.exits[e]
                    database.update(thisroom)
                    return True
            
        # Couldn't find the current room, or the exit does not exist there.
        return False

