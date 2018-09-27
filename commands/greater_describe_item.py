NAME = "describe item"
USAGE = "describe item <id> <description>"
DESCRIPTION = "Set the description of the item <id>, even if you are not holding it."


def COMMAND(console, database, args):
    if len(args) < 2:
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

    i = database.item_by_id(itemid)
    if not i:
        console.msg(NAME + ": no such item")
        return False
    i["desc"] = ' '.join(args[1:])
    database.upsert_item(i)
    console.msg(NAME + ": done")
    return True
