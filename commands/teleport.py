NAME = "teleport"
USAGE = "teleport <room>"
DESCRIPTION = "Teleport to the room (which you own) with ID <room>, or to room 0."


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        dest = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    roomid = console.user["room"]
    thisroom = database.room_by_id(roomid)
    destroom = database.room_by_id(dest)

    if not destroom:
        console.msg(NAME + ": destination room does not exist")
        return False  # The destination room does not exist.
    if not console.user["name"] in destroom["owners"] and not console.user["wizard"] and not destroom["id"] == 0:
        console.msg(NAME + ": you do not have permission to teleport to that room")
        return False
    # Move us to the new room.
    if console.user["name"] in thisroom["users"]:
        thisroom["users"].remove(console.user["name"])
    if console.user["name"] not in destroom["users"]:
        destroom["users"].append(console.user["name"])
    console.broadcast_room(console.user["nick"] + " left the room")
    console.user["room"] = destroom["id"]
    console.broadcast_room(console.user["nick"] + " entered the room")
    database.upsert_room(thisroom)
    database.upsert_room(destroom)
    database.upsert_user(console.user)
    console.command("look", False)
    return True
