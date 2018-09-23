from datatype import Room, User, Item

USAGE = "demote [username]"
DESCRIPTION = "Remove wizard status from yourself or the named user."


def COMMAND(console, database, args):
        if len(args) > 1:
            return False
        
        # Make sure we are logged in.
        # TODO: Check if we have permission to do this.
        if not console.user:
            return False

        if len(args) == 0:
            # Demote ourselves.
            console.user.wizard = False
            database.update(console.user)
        else:
            # Demote the named user.
            targetuser = database.filter(User, {"name": args[0]})
            if len(targetuser) == 0:
                # No such user.
                return False
            targetuser[0].wizard = False
            database.update(targetuser[0])
            
        return True

