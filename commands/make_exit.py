from datatype import Room, User, Item

USAGE = "make exit <destination> <name>"
DESCRIPTION = "Create an exit called <name> in the current room, leading to the room with ID <destination>."

def COMMAND(console, database, args=[]):
        if len(args) < 2:
            return False
        
        dest = int(args[0])
        name = ' '.join(args[1:])
        
        # Make sure we are logged in.
        if not self.user:
            return False
        
        # Check if an exit by this name already exists. Case insensitive.
        thisroom = database.filter(Room, {"id": console.user.room})
        exits = thisroom[0]["exits"]
        if len(exits):
            for e in exits:
                if e["name"].lower() == name.lower():
                    return False # An exit by this name already exists.
        
        # Check if the destination room exists.
        destroom = database.filter(Room, {"id": dest})
        if not len(destroom):
            return False # The destination room does not exist.
        
        # Create our new exit.
        newexit = {"dest": dest, "name": name, "desc": ""}
        thisroom[0].exits.append(newexit)
        
        # Save.
        database.update(thisroom)
        return True

