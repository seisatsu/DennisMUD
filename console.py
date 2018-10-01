import importlib.machinery
import importlib.util
import os
import string
import sys

COMMAND_DIR = "commands/"
ALLOWED_CHARACTERS = string.ascii_letters + string.digits + string.punctuation + ' '


class Console:
    def __init__(self, database, rname, router):
        self.user = None
        self.rname = rname
        self.router = router
        self._database = database
        self._commands = {}
        self._help = {}

        self._load_modules()
        self._build_help()

    def _load_modules(self):
        """
        Enumerate and load available command modules.
        Command modules are stored in COMMAND_DIR, and their filename defines their command name.
        """
        command_modules = os.listdir(COMMAND_DIR)
        for command in command_modules:
            if command.endswith(".py"):
                # Python files in this directory are command modules. Construct modules.
                command_path = os.path.join(os.getcwd(), COMMAND_DIR, command)

                # Different import code recommended for different Python versions.
                if sys.version_info[1] < 5:
                    self._commands[command[:-3]] = \
                        importlib.machinery.SourceFileLoader(command[:-3], command_path).load_module()
                else:
                    spec = importlib.util.spec_from_file_location(command[:-3], command_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    self._commands[command[:-3]] = mod
        print("Registered commands: " + str(list(self._commands.keys())))

    def _build_help(self):
        self._help["all"] = []
        for cmd in self._commands.keys():
            if hasattr(self._commands[cmd], "CATEGORIES"):
                for category in self._commands[cmd].CATEGORIES:
                    if category not in self._help.keys():
                        self._help[category] = []
                    self._help[category].append(cmd)
            self._help["all"].append(cmd)

    def command(self, line, show_command=True):
        """
        Parse and execute a command line, discerning which arguments are part of the command name
        and which arguments should be passed to the command.
        """
        # Strip whitespace from the front and back.
        line = line.strip()

        # Check for illegal characters, except in passwords.
        if line.split(' ')[0] not in ["register", "login"]:
            for c in line:
                if c not in ALLOWED_CHARACTERS:
                    self.msg("command contains illegal characters")
                    return None

        # Split the command line into a list of arguments.
        line = line.split(' ')

        # Find out which part of the line is the command, and which part are its arguments.
        for splitpos in range(len(line)):
            if splitpos == 0:
                if '_'.join(line) in self._commands.keys():
                    # Run the command with no arguments.
                    if show_command:
                        self.msg("> " + ' '.join(line))
                        self.msg('='*20)
                    return self._commands['_'.join(line)].COMMAND(self, self._database, [])
                continue
            if '_'.join(line[:-splitpos]) in self._commands.keys():
                # Run the command and pass arguments.
                if line[0] != "login":
                    if show_command:
                        self.msg("> " + ' '.join(line))
                        self.msg('=' * 20)
                return self._commands['_'.join(line[:-splitpos])].COMMAND(self, self._database, line[-splitpos:])
        if line:
            self.msg("unknown command: " + '_'.join(line))
        return None

    def help(self, line):
        """
        Retrieve the help for a command.
        """
        if not line:
            line = "help"
        if line == "help":
            print("Usage: help <command/category>")
            print("Description: print the help for a command, or list the commands in a category.")
            print("Available Categories: " + ', '.join(sorted(self._help.keys())))
        elif line.replace(' ', '_') in self._commands.keys():
            usage = "Usage: " + self._commands[line.replace(' ', '_')].USAGE
            desc = "Description: " + self._commands[line.replace(' ', '_')].DESCRIPTION
            self.msg(usage)
            self.msg(desc)
        elif line in self._help.keys():
            self.msg("Available commands in category {0}: {1}".format(line, ', '.join(sorted(self._help[line]))))
        else:
            self.msg("help: unknown command or category: " + line)
        return None

    def msg(self, message):
        print(message)
        self.router.message(self.rname, message)
        return True

    def broadcast(self, message):
        print(message)
        self.router.broadcast_all(message)
        return True

    def broadcast_room(self, message):
        print(message)
        self.router.broadcast_room(self.user["room"], message)
        return True
