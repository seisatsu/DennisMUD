NAME = "inventory"
USAGE = "inventory"
DESCRIPTION = "List all items in your inventory."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    for itemid in console.user.inventory:
        i = database.item_by_id(itemid)
        if len(i):
            print(str(i[0].id) + ": " + i[0].name)
    return True
