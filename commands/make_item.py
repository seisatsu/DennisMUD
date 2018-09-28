NAME = "make item"
USAGE = "make item <name>"
DESCRIPTION = "Create a new item called <name> and place it in your inventory."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    name = ' '.join(args)

    # Check if an item by this name already exists. Case insensitive.
    items = list(database.items.find().sort("id", -1))
    if items:
        for i in items:
            if i["name"].lower() == name.lower():
                console.msg(NAME + ": an item by this name already exists")
                return False  # An item by this name already exists.

    # Find the highest numbered currently existing item ID.
    if items:
        lastitem = items[0]["id"]
    else:
        lastitem = -1

    # Create our new item with an ID one higher.
    newitem = {
        "id": lastitem + 1,
        "name": name,
        "desc": "",
        "owners": [console.user["name"]]
    }

    # Add the item to the creator's inventory.
    console.user["inventory"].append(newitem["id"])
    database.upsert_user(console.user)

    # Save.
    database.upsert_item(newitem)
    console.msg(NAME + ": done (id: " + str(newitem["id"]) + ")")
    return True
