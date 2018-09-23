from datatype import Room, User, Item

USAGE = "break item <item>"
DESCRIPTION = "Break the item in your inventory with ID <item>."


def COMMAND(console, database, args):
        if len(args) != 1:
            return False
        
        itemid = int(args[0])
            
        # Make sure we are logged in.
        if not console.user:
            return False
        
        # Check if the item exists.
        i = database.filter(Item, {"id": itemid})
        if len(i):
            i = i[0]
            # Make sure we are holding the item.
            if itemid in console.user.inventory:
                # Delete the item and remove it from our inventory.
                database.delete(i)
                console.user.inventory.remove(itemid)
                database.update(console.user)
                return True
            
        else:
            # No item with that ID exists, or we are not holding it.
            return False

