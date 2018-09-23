from datatype import Room, User, Item

USAGE = "list items"
DESCRIPTION = "List all items in the world."


def COMMAND(console, database, args):
        if len(args) != 0:
            return False
            
        # Make sure we are logged in, and a wizard.
        if not console.user or not console.user.wizard:
            return False
        
        users = database.filter(User, {}).sort("name")
        if len(users):
            for u in users:
                print(u.name+": "+u.nick)

