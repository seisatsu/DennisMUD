from datatype import Room, User, Item

USAGE = "get <item>"
DESCRIPTION = "Pick up the item called <item> from the current room."


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

        # Find the item in the current room.
        for itemid in thisroom["items"]:
            i = database.item_by_id(itemid)
            if i.name.lower() == ' '.join(args).lower():
                # Remove the item from the room and place it in our inventory.
                thisroom["items"].remove(i.id)
                console.user.inventory.append(i.id)
                database.update(thisroom)
                database.update(console.user)
                return True

        return False
