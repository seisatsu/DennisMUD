#####################
# Dennis MUD        #
# shell.py          #
# Copyright 2020    #
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

import builtins
import common
builtins.COMMON = common

from twisted.logger import Logger

# The directory where command modules are stored, relative to this directory.
COMMAND_DIR = "commands/"

# A string list of all characters allowed in user commands.
ALLOWED_CHARACTERS = string.ascii_letters + string.digits + string.punctuation + ' '


class Shell:
    """Shell

    The Shell loads command modules, enumerates help, and provides command access to the user consoles.

    :ivar router: The Router instance, which handles interfacing between the server backend and the user consoles.
    """
    def __init__(self, database, router, log=None):
        """Console Initializer

        :param database: The DatabaseManager instance to use.
        :param router: The Router instance, which handles interfacing between the server backend and the user consoles.
        :param log: Alternative logging facility, if not set.
        """
        self.router = router
        self._log = log or Logger("shell")

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
        self._log.info("Loading command modules...")
        command_modules = os.listdir(COMMAND_DIR)

        # Run through the list of all files in the command directory.
        for command in command_modules:
            # Python files in this directory are command modules. Construct modules.
            if command.endswith(".py") and not command.startswith('_'):
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

        # Check for overlapping command names.
        found_overlaps = []
        for cname in self._commands:
            for cname2 in self._commands:
                if cname == cname2:
                    continue

                # Check if any command starts with the name of any other command,
                # where they are not aliases for each other. This is bad.
                if cname.startswith(cname2 + ' ') and not (
                        (hasattr(self._commands[cname2], "ALIASES") and
                         cname in self._commands[cname2].ALIASES) or
                        (hasattr(self._commands[cname], "ALIASES") and
                         cname2 in self._commands[cname].ALIASES)):

                    # Only warn about each overlap once.
                    if not ([cname, cname2] in found_overlaps or [cname2, cname] in found_overlaps):
                        found_overlaps.append([cname, cname2])
                        self._log.warn("Overlapping command names: {cname}, {cname2}", cname=cname,
                                       cname2=cname2)

        self._log.info("Finished loading command modules.")
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

    def command(self, console, line, show_command=True):
        """Command Handler

        Parse and execute a command line, discerning which arguments are part of the command name
        and which arguments should be passed to the command.

        :param console: The console calling the command.
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
        if line.split(' ')[0] not in ["register", "login", "password"]:
            for c in line:
                if c not in ALLOWED_CHARACTERS:
                    console.msg("Command contains illegal characters.")
                    return None

        # Split the command line into a list of arguments.
        line = line.split(' ')

        # Remove extraneous spaces.
        line = [elem for elem in line if elem != '']

        # Find out which part of the line is the command, and which part is its arguments.
        for splitpos in range(len(line)):
            # Check if the whole line is a command with no arguments.
            if splitpos == 0:
                # Call with no arguments.
                if ' '.join(line).lower() in self._commands.keys():
                    if show_command:
                        console.msg("> " + ' '.join(line))
                        console.msg('='*20)
                    return self.call(console, ' '.join(line).lower(), [])
                continue

            # Only part of the line is a command. Call that segment and pass the rest as arguments.
            if ' '.join(line[:-splitpos]).lower() in self._commands.keys():
                # Log and echo commands to the console that don't involve passwords.
                if line[0] not in ["register", "login", "password"]:
                    if show_command:
                        console.msg("> " + ' '.join(line))
                        console.msg('=' * 20)
                return self.call(console, ' '.join(line[:-splitpos]), line[-splitpos:])

        # We're still here and haven't found a command in this line. Must be gibberish.
        if line:
            console.msg("Unknown command: " + ' '.join(line))

            # Suggest some possible commands that are close to what was typed, if applicable.
            possible = []
            for p in self._commands:
                if p.startswith(' '.join(line)):
                    possible.append(p)
            if possible:
                possible = ', '.join(possible)
                console.msg("Did you mean: " + possible)

        # We didn't find anything.
        return None

    def help(self, console, line):
        """Help Handler

        Retrieve the help for a category or command.

        :param console: The console requesting help.
        :param line: The help line to parse.

        :return: True if succeeded, False if failed.
        """
        # If help was called by itself, assume we want the help for help itself.
        if not line:
            line = "help"

        line = line.lower()

        # Check for command names overlapping category names.
        if line in self._help.keys() and line in self._commands.keys():
            self._log.warn("Command name overlaps with category name: {line}", line=line)

        # Return a help message for the help command, and list available categories.
        if line == "help":
            console.msg("Usage: help <command/category>")
            console.msg("Description: Print the help for a command, or list the commands in a category.")
            console.msg("Available Categories: " + ', '.join(sorted(self._help.keys())))

        # Return a formatted help message for the named category.
        # Thanks to:
        # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
        # https://stackoverflow.com/questions/9989334/create-nice-column-output-in-python
        elif line in self._help.keys():
            cn = self._database.defaults["help"]["columns"]
            cols = [sorted(self._help[line])[i:i + cn] for i in range(0, len(sorted(self._help[line])), cn)]
            col_width = max(len(word) for row in cols for word in row) + 2  # padding
            console.msg("Available commands in category {0}:".format(line))
            for row in cols:
                console.msg("".join(word.ljust(col_width) for word in row), True)

        # Return a help message for the named command.
        elif line in self._commands.keys():
            # Return a help message for the named command.
            usage = "Usage: " + self._commands[line].USAGE
            desc = "Description: " + self._commands[line].DESCRIPTION

            # Enumerate the aliases and list them at the end of the description.
            alias_list = ""
            if hasattr(self._commands[line], "ALIASES"):
                alias_list += (', '.join(self._commands[line].ALIASES))
            if hasattr(self._commands[line], "SPECIAL_ALIASES"):
                if alias_list:
                    alias_list += ', '
                alias_list += (', '.join(self._commands[line].SPECIAL_ALIASES))
            if alias_list:
                desc += "\n\nCommand Aliases: " + alias_list
            console.msg(usage)
            console.msg(desc)

        # Couldn't find anything.
        else:
            console.msg("help: Unknown command or category: " + line)
            return False

        # Success.
        return True

    def usage(self, console, line):
        """Usage Handler

        Retrieve just the usage string for a command.

        :param console: The console requesting help.
        :param line: The help line to parse.

        :return: True if succeeded, False if failed.
        """
        # If usage was called by itself, assume we want the usage string for usage itself.
        if not line:
            line = "usage"

        line = line.lower()

        # Return a usage string for the usage command.
        if line == "usage":
            console.msg("Usage: usage <command>")

        # Return a usage string for the named command.
        elif line in self._commands.keys():
            usage = "Usage: " + self._commands[line].USAGE
            console.msg(usage)

        # Couldn't find anything.
        else:
            console.msg("usage: Unknown command: " + line)
            return False

        # Success.
        return True

    def msg_user(self, username, message):
        """Send a message to a particular user.

        :param username: The username of the user to message.
        :param message: The message to send.

        :return: True if succeeded, False if failed.
        """
        for u in self.router.users:
            if self.router.users[u]["console"].user and \
                    self.router.users[u]["console"].user["name"] == username.lower():
                self.router.users[u]["console"].msg(message)
                return True
        return False

    def broadcast(self, message, exclude=None):
        """Broadcast Message

        Send a message to all users connected to consoles.

        :param message: The message to send.
        :param exclude: If set, username to exclude from broadcast.

        :return: True
        """
        self._log.info(message)
        self.router.broadcast_all(message, exclude)
        return True

    def broadcast_room(self, console, message, exclude=None):
        """Broadcast Message to Room

        Send a message to all users who are in the same room as the user connected to this console.

        :param console: The console sending the message.
        :param message: The message to send.
        :param exclude: If set, username to exclude from broadcast.

        :return: True
        """
        self._log.info(message)
        self.router.broadcast_room(console.user["room"], message, exclude)
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
                    self.router.users[u]["console"].user["name"].lower() == username.lower():
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
                    self.router.users[u]["console"].user["nick"].lower() == nickname.lower():
                return self.router.users[u]["console"].user
        return self._database.user_by_nick(nickname.lower())

    def console_by_username(self, username):
        """Get the console of a user by their username.

        :return: Console if succeeded, None if failed.
        """
        for u in self.router.users:
            if self.router.users[u]["console"].user and \
                    self.router.users[u]["console"].user["name"].lower() == username.lower():
                return self.router.users[u]["console"]

    def call(self, console, command, args):
        """Call a command, making sure it isn't disabled. (Unless we're a wizard, then it doesn't matter.)

        :param console: The console calling the command.
        :param command: The name of the command to call.
        :param args: Arguments to the command.

        :return: True if succeeded, False if failed
        """
        if command in self._disabled_commands and not console.user["wizard"]:
            console.msg("{0}: Command disabled.".format(command))
            return False
        return self._commands[command].COMMAND(console, args)
