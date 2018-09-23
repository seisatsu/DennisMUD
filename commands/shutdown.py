import sys
from datatype import Room, User, Item

USAGE = "shutdown"
DESCRIPTION = "Shut down the server."


def COMMAND(console, database, args):
        if len(args) != 0:
            return False
            
        # Make sure we are logged in, and a wizard.
        if not console.user or not console.user.wizard:
            return False
        
        # TODO: Graceful shutdown.
        sys.exit(0)

