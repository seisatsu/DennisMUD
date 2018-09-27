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

    try:
        itemid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Check if the item exists.
    i = database.item_by_id(itemid)
    if i:
        # Make sure we are holding the item.
        if itemid in console.user["inventory"]:
            # Delete the item and remove it from our inventory.
            database.delete_item(i)
            console.user["inventory"].remove(itemid)
            database.upsert_user(console.user)
            console.msg(NAME + ": done")
            return True
        else:
            # We are not holding that item.
            console.msg(NAME + ": not holding item")
            return False

    else:
        # No item with that ID exists.
        console.msg(NAME + ": no such item")
        return False
