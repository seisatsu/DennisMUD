from datatype import Room, User, Item

USAGE = "list rooms"
DESCRIPTION = "List all rooms in the world."


def COMMAND(console, database, args):
        if len(args) != 0:
            return False
            
        # Make sure we are logged in, and a wizard.
        if not console.user or not console.user.wizard:
            return False
        
        rooms = database.filter(Room, {}).sort("id")
        if len(rooms):
            for r in rooms:
                print(str(r.id)+": "+r.name)

