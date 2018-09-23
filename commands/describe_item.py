from datatype import Room, User, Item

USAGE = "describe item <id> <description>"
DESCRIPTION = "Set the description of the item <id> which you are holding."


def COMMAND(console, database, args):
    if len(args) < 2:
        return False

    # Make sure we are logged in.
    if not console.user:
        return False

    itemid = int(args[0])

    # Make sure we are holding the item.
    if itemid not in console.user.inventory:
        return False

    i = database.item_by_id(itemid)
    i.desc = ' '.join(args[1:])
    database.update(i)
    return True
