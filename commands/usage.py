NAME = "usage"
CATEGORIES = ["info"]
USAGE = "usage <command>"
DESCRIPTION = "Print the usage info for a command."


def COMMAND(console, database, args):
    return console.usage(' '.join(args))
