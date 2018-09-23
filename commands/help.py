NAME = "help"
USAGE = "help <command>"
DESCRIPTION = "Print the help info for a command."


def COMMAND(console, database, args):
    console.help(' '.join(args))
