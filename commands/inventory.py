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

    for itemid in console.user["inventory"]:
        i = database.item_by_id(itemid)
        if i:
            console.msg(i["name"] + " (" + str(i["id"]) + ")")
        else:
            console.msg(NAME + ": empty")
    return True
