import hashlib
from datatype import Room, User, Item

def COMMAND(database, args):
        # args = [username, password]
        
        # Register a new user.
        check = database.filter(
            User, {
                "name": args[0]
            }
        )
        if len(check) != 0: # User already exists.
            return False
        
        # Create new user.
        newuser = User({
            "name": args[0],
            "nick": args[0],
            "desc": "",
            "passhash": hashlib.sha256(args[1].encode()).hexdigest(),
            "online": False,
            "room": 0,
            "inventory": [],
            "wizard": False
        })
        
        # Save.
        database.insert(newuser)
        return True

