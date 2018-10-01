NAME = "requisition"
CATEGORIES = ["items"]
USAGE = "requisition <item>"
DESCRIPTION = "Obtain the item (which you own) with id <item>, regardless of where it is."


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
        if console.user["name"] not in i["owners"] and not console.user["wizard"]:
            console.msg(NAME + ": you do not have permission to requisition that item")
            return False

        # If the item is in a room's item list, remove it.
        rooms = database.rooms.find()
        if rooms:
            for r in rooms:
                if itemid in r["items"]:
                    r["items"].remove(itemid)
                    database.upsert_room(r)

        # If the item is in someone's inventory, remove it.
        users = database.users.find()
        if users:
            for u in users:
                if itemid in u["inventory"]:
                    u["inventory"].remove(itemid)
                    database.upsert_user(u)

        # Place the item in our inventory.
        console.user["inventory"].append(itemid)
        database.upsert_user(console.user)
        console.msg("requisitioned item " + i["name"] + " (" + str(i["id"]) + ")")
        return True

    else:
        # No item with that ID exists.
        console.msg(NAME + ": no such item")
        return False
