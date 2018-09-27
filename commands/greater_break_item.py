NAME = "greater break item"
USAGE = "greater break item <item>"
DESCRIPTION = "Break the item with ID <item> even if you aren't holding it."


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False
    if not console.user["wizard"]:
        console.msg(NAME + ": you do not have permission to use this command")
        return False

    try:
        itemid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    # Check if the item exists.
    i = database.item_by_id(itemid)
    if i:
        # Delete the item.
        database.delete_item(i)

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

        console.msg(NAME + ": done")
        return True

    else:
        # No item with that ID exists.
        console.msg(NAME + ": no such item")
        return False
