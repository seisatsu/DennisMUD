from datatype import Room, User, Item

USAGE = "drop <item>"
DESCRIPTION = "Drop the item called <item> into the current room."


def COMMAND(console, database, args):
        if len(args) == 0:
            return False
            
        # Make sure we are logged in.
        if not console.user:
            return False

        # Find the current room.
        thisroom = database.filter(Room, {"id": console.user.room})
        if not len(thisroom):
            return False  # The current room does not exist?!
        thisroom = thisroom[0]

        # Find the item in our inventory.
        for itemid in console.user.inventory:
            i = database.item_by_id(itemid)
            if i.name.lower() == ' '.join(args).lower():
                # Remove the item from our inventory and place it in the room.
                console.user.inventory.remove(i.id)
                thisroom["items"].append(i.id)
                database.update(console.user)
                database.update(thisroom)
                return True

        return False
