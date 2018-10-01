NAME = "help"
CATEGORIES = ["info"]
USAGE = "help <command/category>"
DESCRIPTION = "Print the help for a command, or list the commands in a category."


def COMMAND(console, database, args):
    return console.help(' '.join(args))
