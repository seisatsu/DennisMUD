NAME = "locate user"
USAGE = "locate user <name>"
DESCRIPTION = "Find out what room the user <name> is in."


def COMMAND(console, database, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    u = database.user_by_name(args[0].lower())
    if not u:
        console.msg(NAME + ": no such user")
        return False

    # check the user is offline.
    if not u["online"]:
        console.msg("User " + u["name"] + " is offline")
        return True
    else:
        for r in database.rooms.find():
            if u["name"] in r["users"]:
                console.msg("User " + u["name"] + " is in room " + r["name"] + " (" + str(r["id"]) + ")")
                return True

    # Couldn't find the user.
    console.msg(NAME + ": Warning: user is online but could not be found")
    return False
