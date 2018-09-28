NAME = "rename item"
USAGE = "rename item <id> <name>"
DESCRIPTION = "Set the name of the item <id> which you are holding."


def COMMAND(console, database, args):
    if len(args) < 2:
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

    # Make sure we are holding the item.
    if itemid not in console.user["inventory"] and not console.user["wizard"]:
        console.msg(NAME + ": no such item in inventory")
        return False

    i = database.item_by_id(itemid)

    # Make sure we are the item's owner.
    if console.user["name"] not in i["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this item")
        return False

    i["name"] = ' '.join(args[1:])
    database.upsert_item(i)
    console.msg(NAME + ": done")
    return True
