from datatype import Room, User, Item

USAGE = "make room <name>"
DESCRIPTION = "Create a room called <name>."


def COMMAND(console, database, args):
        if len(args) == 0:
            return False
        
        name = ' '.join(args)
            
        # Make sure we are logged in.
        if not console.user:
            return False
        
        # Check if a room by this name already exists. Case insensitive.
        rooms = database.filter(Room, {})
        if len(rooms):
            for r in rooms:
                if r["name"].lower() == name.lower():
                    return False # A room by this name already exists.
        
        # Find the highest numbered currently existing room ID.
        if len(rooms):
            lastroom = rooms.sort("id")[-1]["id"]
        else:
            lastroom = -1
        
        # Create our new room with an ID one higher.
        newroom = Room({
            "owner": console.user.name,
            "id": lastroom + 1,
            "name": name,
            "desc": "",
            "users": [],
            "exits": [],
            "items": []
        })
        
        # Save.
        database.insert(newroom)
        return True

