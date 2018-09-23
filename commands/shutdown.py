import sys

NAME = "shutdown"
USAGE = "shutdown"
DESCRIPTION = "Shut down the server."


def COMMAND(console, database, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user:
        console.msg("shutdown: must be logged in first")
        return False
    if not console.user.wizard:
        console.msg("shutdown: you do not have permission to use this command")
        return False

    # TODO: Graceful shutdown.
    sys.exit(0)
