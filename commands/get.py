NAME = "get"
USAGE = "get <item>"
DESCRIPTION = "Pick up the item called <item> from the current room."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Look for the current room.
    thisroom = database.room_by_id(console.user["room"])
    if not thisroom:
        console.msg("warning: current room does not exist")
        return False  # The current room does not exist?!

    # Find the item in the current room.
    for itemid in thisroom["items"]:
        i = database.item_by_id(itemid)
        if i["name"].lower() == ' '.join(args).lower():
            # Remove the item from the room and place it in our inventory.
            thisroom["items"].remove(i["id"])
            console.user["inventory"].append(i["id"])
            database.upsert_room(thisroom)
            database.upsert_user(console.user)
            console.msg("picked up " + ' '.join(args))
            return True

    console.msg(NAME + ": no such item")
    return False
