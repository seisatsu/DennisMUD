import hashlib

NAME = "register"
USAGE = "register <username> <password>"
DESCRIPTION = "Register a new user with <username> and <password>."


def COMMAND(console, database, args):
    # args = [username, password]
    if len(args) != 2:
        console.msg("Usage: " + USAGE)
        return False

    # Register a new user.
    check = database.users.find_one(
        {
            "name": args[0]
        }
    )
    if check:  # User already exists.
        console.msg(NAME + ": user already exists")
        return False

    # Create new user.
    newuser = {
        "name": args[0].lower(),
        "nick": args[0],
        "desc": "",
        "passhash": hashlib.sha256(args[1].encode()).hexdigest(),
        "online": False,
        "room": 0,
        "inventory": [],
        "keys": [],
        "wizard": False
    }

    # Save.
    database.upsert_user(newuser)
    console.msg("registered user \"" + newuser["name"] + "\"")
    return True
