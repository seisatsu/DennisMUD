NAME = "break item"
USAGE = "break item <item>"
DESCRIPTION = "Break the item in your inventory with ID <item>."


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    itemid = int(args[0])

    # Check if the item exists.
    i = database.item_by_id(itemid)
    if i:
        # Make sure we are holding the item.
        if itemid in console.user.inventory:
            # Delete the item and remove it from our inventory.
            database.delete(i)
            console.user.inventory.remove(itemid)
            database.update(console.user)
            console.msg(NAME + ": done")
            return True

    else:
        # No item with that ID exists, or we are not holding it.
        console.msg(NAME + ": no such item in inventory")
        return False
