from datatype import Room, User, Item

USAGE = "promote [username]"
DESCRIPTION = "Elevate yourself or the named user to wizard status."

def COMMAND(console, database, args=[]):
        if len(args) > 1:
            return False
        
        # Make sure we are logged in.
        # TODO: Check if we have permission to do this.
        if not console.user:
            return False

        if len(args) == 0:
            # Upgrade ourselves to wizard.
            console.user.wizard = True
            database.update(console.user)
        else:
            # Upgrade the named user to wizard.
            targetuser = database.filter(User, {"name": args[0]})
            if len(targetuser) == 0:
                # No such user.
                return False
            targetuser[0].wizard = True
            database.update(targetuser[0])
            
        return True

