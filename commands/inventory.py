from datatype import Room, User, Item

USAGE = "inventory"
DESCRIPTION = "List all items in your inventory."


def COMMAND(console, database, args):
        if len(args) != 0:
            return False
            
        # Make sure we are logged in.
        if not console.user:
            return False
        
        for itemid in console.user.inventory:
            i = database.filter(Item, {"id": itemid})
            if len(i):
                print(str(i[0].id)+": "+i[0].name)
        return True
