NAME = "list items"
USAGE = "list items"
DESCRIPTION = "List all items in the world that you own."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    items = database.items.find().sort("id", 1)
    found_something = False
    if items.count():
        for i in items:
            if console.user["name"] in i["owners"] or console.user["wizard"]:
                # We either own this one, or we are a wizard.
                console.msg(str(i["id"]) + ": " + i["name"])
                found_something = True
    if not found_something:
        if console.user["wizard"]:
            console.msg(NAME + ": there are no items")
        else:
            console.msg(NAME + ": you do not own any items")

    return True
