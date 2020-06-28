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

from twisted.logger import Logger

# The directory where command modules are stored, relative to this directory.
COMMAND_DIR = "commands/"

# A string list of all characters allowed in user commands.
ALLOWED_CHARACTERS = string.ascii_letters + string.digits + string.punctuation + ' '


class Console:
    """Console

    Each instance of the console corresponds to a single user session. The console handles user-command interaction.

    :ivar user: TinyDB user document for the currently logged in user, if any.
    :ivar rname: The name used by the router for this console.
    :ivar router: The Router instance, which handles interfacing between the server backend and the user consoles.
    """
    def __init__(self, database, rname, router, log=None):
        """Console Initializer

        :param database: The DatabaseManager instance to use.
        :param rname: The name used by the router for this console.
        :param router: The Router instance, which handles interfacing between the server backend and the user consoles.
        :param log: Alternative logging facility, if set.
        """
        self.user = None
        self.rname = rname
        self.router = router
        self._log = log or Logger("console:{0}".format(rname))

        self._database = database
        self._commands = {}
        self._help = {}
        self._special_aliases = {}
        self._disabled_commands = []

        self._load_modules()
        self._build_help()

    def _load_modules(self):
        """Enumerate and load available command modules.

        Command modules are stored in COMMAND_DIR, and their filename defines their command name.

        :return: True
        """
        self._log.info("loading command modules")
        command_modules = os.listdir(COMMAND_DIR)
        for command in command_modules:
            if command.endswith(".py"):
                # Python files in this directory are command modules. Construct modules.
                command_path = os.path.join(os.getcwd(), COMMAND_DIR, command)
                cname = command[:-3].replace('_', ' ')

                # Different import code recommended for different Python versions.
                if sys.version_info[1] < 5:
                    self._commands[cname] = \
                        importlib.machinery.SourceFileLoader(cname, command_path).load_module()
                else:
                    spec = importlib.util.spec_from_file_location(cname, command_path)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    self._commands[cname] = mod

                # Set up Aliases for this command.
                # Aliases are alternative names for a command.
                if hasattr(self._commands[cname], "ALIASES"):
                    for alias in self._commands[cname].ALIASES:
                        self._commands[alias] = self._commands[cname]

                # Set up Special Aliases for this command.
                # Special Aliases are single character aliases that don't need a space after them.
                if hasattr(self._commands[cname], "SPECIAL_ALIASES"):
                    for special_alias in self._commands[cname].SPECIAL_ALIASES:
                        self._special_aliases[special_alias] = cname

        self._log.info("finished loading command modules")
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
                    if not self._commands[cmd].NAME in self._help[category]:
                        self._help[category].append(self._commands[cmd].NAME)
            if not self._commands[cmd].NAME in self._help["all"]:
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
        # Return if we got an empty line.
        if not line:
            return None

        # Strip whitespace from the front and back.
        line = line.strip()

        # Process any special aliases.
        if line[0] in self._special_aliases:
            line = line.replace(line[0], self._special_aliases[line[0]]+' ', 1)

        # Check for illegal characters, except in passwords.
        if line.split(' ')[0] not in ["register", "login"]:
            for c in line:
                if c not in ALLOWED_CHARACTERS:
                    self.msg("command contains illegal characters")
                    return None

        # Split the command line into a list of arguments.
        line = line.split(' ')

        # Remove extraneous spaces.
        line = [elem for elem in line if elem != '']

        # Find out which part of the line is the command, and which part are its arguments.
        for splitpos in range(len(line)):
            if splitpos == 0:
                if ' '.join(line).lower() in self._commands.keys():
                    # Run the command with no arguments.
                    if show_command:
                        self.msg("> " + ' '.join(line))
                        self.msg('='*20)
                    return self._call(' '.join(line).lower(), [])
                continue
            if ' '.join(line[:-splitpos]).lower() in self._commands.keys():
                # Run the command and pass arguments.
                if line[0] != "login":
                    if show_command:
                        self.msg("> " + ' '.join(line))
                        self.msg('=' * 20)
                return self._call(' '.join(line[:-splitpos]), line[-splitpos:])
        if line:
            self.msg("unknown command: " + ' '.join(line))
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
        line = line.lower()
        if line == "help":
            # Return a help message for the help command, and list available categories.
            self.msg("Usage: help <command/category>")
            self.msg("Description: Print the help for a command, or list the commands in a category.")
            self.msg("Available Categories: " + ', '.join(sorted(self._help.keys())))
        elif line in self._commands.keys():
            # Return a help message for the named command.
            usage = "Usage: " + self._commands[line].USAGE
            desc = "Description: " + self._commands[line].DESCRIPTION
            self.msg(usage)
            self.msg(desc)
        elif line in self._help.keys():
            # Return a formatted help message for the named category.
            # Thanks to:
            # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
            # https://stackoverflow.com/questions/9989334/create-nice-column-output-in-python
            cn = self._database.defaults["help"]["columns"]
            cols = [sorted(self._help[line])[i:i + cn] for i in range(0, len(sorted(self._help[line])), cn)]
            col_width = max(len(word) for row in cols for word in row) + 2  # padding
            self.msg("Available commands in category {0}:".format(line))
            for row in cols:
                self.msg("".join(word.ljust(col_width) for word in row), True)
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
        line = line.lower()
        if line == "usage":
            # Return a usage string for the usage command.
            self.msg("Usage: usage <command>")
        elif line in self._commands.keys():
            # Return a usage string for the named command.
            usage = "Usage: " + self._commands[line].USAGE
            self.msg(usage)
        else:
            # Couldn't find anything.
            self.msg("usage: unknown command: " + line)
            return False

        return True

    def msg(self, message, _nbsp=False):
        """Send Message

        Send a message to the user connected to this console.

        :param message: The message to send.
        :param _nbsp: Will insert non-breakable spaces for formatting on the websocket frontend.
        :return: True
        """
        if self.router.single_user:
            print(message)
        else:
            self._log.info(message)
        self.router.message(self.rname, message, _nbsp)
        return True

    def broadcast(self, message):
        """Broadcast Message

        Send a message to all users connected to consoles.

        :param message: The message to send.
        :return: True
        """
        self._log.info(message)
        self.router.broadcast_all(message)
        return True

    def broadcast_room(self, message):
        """Broadcast Message to Room

        Send a message to all users who are in the same room as the user connected to this console.

        :param message: The message to send.
        :return: True
        """
        self._log.info(message)
        self.router.broadcast_room(self.user["room"], message)
        return True

    def user_by_name(self, username):
        """Get a user by their name.

        It is necessary to modify user records through the console before updating the database, if they are logged in.
        Otherwise their database record will be overwritten next time something is changed in their console record.
        If the user is logged in, return their console record.
        Otherwise, return their record directly from the database.

        :return: Console or Database User Document, or None
        """
        for u in self.router.users:
            if self.router.users[u]["console"].user and \
                    self.router.users[u]["console"].user["name"] == username.lower():
                return self.router.users[u]["console"].user
        return self._database.user_by_name(username.lower())

    def user_by_nick(self, nickname):
        """Get a user by their nickname.

        It is necessary to modify user records through the console before updating the database, if they are logged in.
        Otherwise their database record will be overwritten next time something is changed in their console record.
        If the user is logged in, return their console record.
        Otherwise, return their record directly from the database.

        :return: Console or Database User Document, or None
        """
        for u in self.router.users:
            if self.router.users[u]["console"].user and \
                    self.router.users[u]["console"].user["nick"] == nickname.lower():
                return self.router.users[u]["console"].user
        return self._database.user_by_nick(nickname.lower())

    def _call(self, command, args):
        """Call a command, making sure it isn't disabled. (Unless we're a wizard, then it doesn't matter.)

        :return: True if succeeded, False if failed
        """
        if command in self._disabled_commands and not self.user["wizard"]:
            self.msg(command + ": command disabled")
            return False
        return self._commands[command].COMMAND(self, self._database, args)
