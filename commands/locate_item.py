NAME = "locate item"
CATEGORIES = ["items"]
USAGE = "locate item <id>"
DESCRIPTION = "Find out what room the item <id> (which we own) is in, or who is holding it."


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

    i = database.item_by_id(itemid)
    if not i:
        console.msg(NAME + ": no such item")
        return False

    # Make sure we are the item's owner.
    if console.user["name"] not in i["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this item")
        return False

    # check if we are holding the item.
    if itemid in console.user["inventory"]:
        console.msg("Item " + i["name"] + " (" + str(i["id"]) + ") is in your inventory")
        return True

    # check if someone else is holding the item.
    for u in database.users.find():
        if itemid in u["inventory"]:
            console.msg("Item " + i["name"] + " (" + str(i["id"]) + ") is in " + u["name"] + "'s your inventory")
            return True

    # check if the item is in a room.
    for r in database.rooms.find():
        if itemid in r["items"]:
            console.msg("Item " + i["name"] + " (" + str(i["id"]) + ") is in room " +
                        r["name"] + " (" + str(r["id"]) + ")")
            return True

    # Couldn't find the item.
    console.msg(NAME + ": Warning: item exists but could not be found")
    return False
