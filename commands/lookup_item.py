NAME = "lookup item"
USAGE = "lookup item <name>"
DESCRIPTION = "Find the ID of the item <name>."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    items = database.items.find()
    for i in items:
        if i["name"].lower() == ' '.join(args).lower():
            console.msg(i["name"] + ": " + str(i["id"]))
            return True

    # Couldn't find the item.
    console.msg(NAME + ": no such item")
    return False
