from datatype import Room, User, Item

USAGE = "help <command>"
DESCRIPTION = "Print the help info for a command."


def COMMAND(console, database, args):
        if len(args) == 0:
            return False

        console.help(' '.join(args))
