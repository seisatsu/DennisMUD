from datatype import Room, User, Item

USAGE = "make item <name>"
DESCRIPTION = "Create an item called <name> and place it in your inventory."


def COMMAND(console, database, args):
        if len(args) == 0:
            return False
        
        name = ' '.join(args)
            
        # Make sure we are logged in.
        if not console.user:
            return False
        
        # Check if an item by this name already exists. Case insensitive.
        items = database.filter(Item, {})
        if len(items):
            for i in items:
                if i["name"].lower() == name.lower():
                    return False # An item by this name already exists.
        
        # Find the highest numbered currently existing item ID.
        if len(items):
            lastitem = items.sort("id")[-1]["id"]
        else:
            lastitem = -1
        
        # Create our new item with an ID one higher.
        newitem = Item({
            "id": lastitem + 1,
            "name": name,
            "desc": ""
        })
        
        # Add the item to the creator's inventory.
        console.user.inventory.append(newitem.id)
        database.update(console.user)
        
        # Save.
        database.insert(newitem)
        return True

