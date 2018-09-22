from datatype import Room, User, Item

USAGE = "greater break item <item>"
DESCRIPTION = "Break the item with ID <item> even if you aren't holding it."

def COMMAND(console, database, args=[]):
        if len(args) != 1:
            return False
        
        itemid = int(args[0])
            
        # Make sure we are logged in, and a wizard.
        if not console.user or not console.user.wizard:
            return False
        
        # Check if the item exists.
        i = database.filter(Item, {"id": itemid})
        if len(i):
            i = i[0]
            # Delete the item.
            database.delete(i)
            
            # If the item is in a room's item list, remove it.
            rooms = database.filter(Room, {})
            if len(rooms):
                for r in rooms:
                    if itemid in r["items"]:
                        r["items"].remove(itemid)
                        database.update(r)
            
            # If the item is in someone's inventory, remove it.
            users = database.filter(User, {})
            if len(users):
                for u in users:
                    if itemid in u["inventory"]:
                        u["inventory"].remove(itemid)
                        database.update(u)
            
            return True
            
        else:
            # No item with that ID exists.
            return False

