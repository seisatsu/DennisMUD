NAME = "drop"
CATEGORIES = ["items"]
USAGE = "drop <item>"
DESCRIPTION = "Drop the item called <item> into the current room."


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

    # Find the item in our inventory.
    for itemid in console.user["inventory"]:
        i = database.item_by_id(itemid)
        if i["name"].lower() == ' '.join(args).lower():
            # Remove the item from our inventory and place it in the room.
            console.user["inventory"].remove(i["id"])
            thisroom["items"].append(i["id"])
            database.upsert_user(console.user)
            database.upsert_room(thisroom)
            console.broadcast_room(console.user["nick"] + " dropped " + ' '.join(args))
            return True

    console.msg(NAME + ": no such item in inventory")
    return False
