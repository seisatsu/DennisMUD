#####################
# Dennis MUD        #
# console.py        #
# Copyright 2018    #
# Michael D. Reiley #
#####################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

import importlib.machinery
import importlib.util
import os
import string
import sys

# The directory where command modules are stored, relative to this directory.
COMMAND_DIR = "commands/"

# A string list of all characters allowed in user commands.
ALLOWED_CHARACTERS = string.ascii_letters + string.digits + string.punctuation + ' '


class Console:
    """Console

    Each instance of the console corresponds to a single user session. The console handles user-command interaction.

    Attributes:
        user: PyMongo user document for the currently logged in user, if any.
        rname: The name used by the router for this console.
        router: The Router instance, which handles interfacing between the server backend and the user consoles.
    """
    def __init__(self, database, rname, router):
        """Console Initializer

        :param database: The DatabaseManager instance to use.
        :param rname: The name used by the router for this console.
        :param router: The Router instance, which handles interfacing between the server backend and the user consoles.
        """
        self.user = None
        self.rname = rname
        self.router = router
        self._database = database
        self._commands = {}
        self._help = {}

        self._load_modules()
        self._build_help()

    def _load_modules(self):
        """Enumerate and load available command modules.

        Command modules are stored in COMMAND_DIR, and their filename defines their command name.

        :return: True
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
        return True

    def _build_help(self):
        """Enumerate available help categories and commands.

        Categories and commands are read from constants in the command modules.

        :return: True
        """
        self._help["all"] = []
        for cmd in self._commands.keys():
            if hasattr(self._commands[cmd], "CATEGORIES"):
                for category in self._commands[cmd].CATEGORIES:
                    if category not in self._help.keys():
                        self._help[category] = []
                    self._help[category].append(self._commands[cmd].NAME)
            self._help["all"].append(self._commands[cmd].NAME)

        return True

    def command(self, line, show_command=True):
        """Command Handler

        Parse and execute a command line, discerning which arguments are part of the command name
        and which arguments should be passed to the command.

        :param line: The command line to parse.
        :param show_command: Whether or not to echo the command being executed in the console.
        :return: Command result or None.
        """
        # Strip whitespace from the front and back.
        line = line.strip()

        # Setup some aliases.
        if line.startswith('\"'):
            line.replace('\"', "say ", 1)
        elif line.startswith('#'):
            line.replace('#', "chat ", 1)
        elif line.startswith('.'):
            line.replace('.', "message ", 1)
        elif line.startswith('msg '):
            line.replace('msg ', "message ", 1)
        elif line.startswith(':'):
            line.replace(':', "action ", 1)
        elif line.startswith('emote '):
            line.replace('emote ', "action ", 1)

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
        """Help Handler

        Retrieve the help for a category or command.

        :param line: The help line to parse.
        :return: True if succeeded, False if failed.
        """
        if not line:
            # If help was called by itself, assume we want the help for help itself.
            line = "help"
        if line == "help":
            # Return a help message for the help command, and list available categories.
            self.msg("Usage: help <command/category>")
            self.msg("Description: Print the help for a command, or list the commands in a category.")
            self.msg("Available Categories: " + ', '.join(sorted(self._help.keys())))
        elif line.replace(' ', '_') in self._commands.keys():
            # Return a help message for the named command.
            usage = "Usage: " + self._commands[line.replace(' ', '_')].USAGE
            desc = "Description: " + self._commands[line.replace(' ', '_')].DESCRIPTION
            self.msg(usage)
            self.msg(desc)
        elif line in self._help.keys():
            # Return a help message for the named category.
            self.msg("Available commands in category {0}: {1}".format(line, ', '.join(sorted(self._help[line]))))
        else:
            # Couldn't find anything.
            self.msg("help: unknown command or category: " + line)
            return False

        return True

    def usage(self, line):
        """Usage Handler

        Retrieve just the usage string for a command.

        :param line: The help line to parse.
        :return: True if succeeded, False if failed.
        """
        if not line:
            # If usage was called by itself, assume we want the usage string for usage itself.
            line = "usage"
        if line == "usage":
            # Return a usage string for the usage command.
            self.msg("Usage: usage <command>")
        elif line.replace(' ', '_') in self._commands.keys():
            # Return a usage string for the named command.
            usage = "Usage: " + self._commands[line.replace(' ', '_')].USAGE
            self.msg(usage)
        else:
            # Couldn't find anything.
            self.msg("usage: unknown command: " + line)
            return False

        return True

    def msg(self, message):
        """Send Message

        Send a message to the user connected to this console.

        :param message: The message to send.
        :return: True
        """
        print(message)
        self.router.message(self.rname, message)
        return True

    def broadcast(self, message):
        """Broadcast Message

        Send a message to all users connected to consoles.

        :param message: The message to send.
        :return: True
        """
        print(message)
        self.router.broadcast_all(message)
        return True

    def broadcast_room(self, message):
        """Broadcast Message to Room

        Send a message to all users who are in the same room as the user connected to this console.

        :param message: The message to send.
        :return: True
        """
        print(message)
        self.router.broadcast_room(self.user["room"], message)
        return True
