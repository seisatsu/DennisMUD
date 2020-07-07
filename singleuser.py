#####################
# Dennis MUD        #
# singleuser.py     #
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

import sys

# Check Python version.
if sys.version_info[0] != 3:
    print("Not Starting: Dennis requires Python 3")
    sys.exit(1)

from lib import console as _console
from lib import database as _database
from lib import shell as _shell

import json
import os
import pdb
import shutil
import traceback

from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory


VERSION = "v0.0.2a-alpha"


class Router:
    """Dummy Router

    This provides just enough functionality for Dennis to run with one player.
    """
    def __init__(self, log):
        self.users = {}
        self.shell = None
        self.single_user = True
        self.log = log

    def message(self, peer, msg, _nbsp=None):
        pass

    def broadcast_all(self, msg, exclude=None):
        if not exclude:
            self.log.write(msg)

    def broadcast_room(self, room, msg, exclude=None):
        if not exclude:
            self.log.write(msg)


class Log:
    """Stand-in for Twisted's logger.

    Logs to STDOUT, and optionally to a file.
    Filters out unwanted messages using a log level setting.
    """
    def __init__(self, loglevel, logfile, waitoncritical):
        """Single User Mode Log Initializer

        :param loglevel: The log level to use. One of: debug, info, warn, error, critical, in descending verbosity.
        :param logfile: The open file to log to.
        :param waitoncritical: Whether to wait for the enter key before exiting on a critical error. Nice for Windows.
        """
        self._loglevel = loglevel
        self._logfile = logfile
        self._waitoncritical = waitoncritical

    def debug(self, msg, **kwargs):
        """Write a debug level message to the console and/or the log file.
        """
        if self._loglevel in ["debug"]:
            print("[singleuser#debug]", msg.format(**kwargs))
            if self._logfile:
                self._logfile.write("[singleuser#debug] " + msg.format(**kwargs) + "\n")

    def info(self, msg, **kwargs):
        """Write an info level message to the console and/or the log file.
        """
        if self._loglevel in ["debug", "info"]:
            print("[singleuser#info]", msg.format(**kwargs))
            if self._logfile:
                self._logfile.write("[singleuser#info] " + msg.format(**kwargs) + "\n")

    def warn(self, msg, **kwargs):
        """Write a warn level message to the console and/or the log file.
        """
        if self._loglevel in ["debug", "info", "warn"]:
            print("[singleuser#warn]", msg.format(**kwargs))
            if self._logfile:
                self._logfile.write("[singleuser#warn] " + msg.format(**kwargs) + "\n")

    def error(self, msg, **kwargs):
        """Write an error level message to the console and/or the log file.
        """
        if self._loglevel in ["debug", "info", "warn", "error"]:
            print("[singleuser#error]", msg.format(**kwargs))
            if self._logfile:
                self._logfile.write("[singleuser#error] " + msg.format(**kwargs) + "\n")

    def critical(self, msg, **kwargs):
        """Write a critical level message to the console and/or the log file.

        All log levels include critical, so these messages cannot be disabled.
        """
        print("[singleuser#critical]", msg.format(**kwargs))
        if self._logfile:
            self._logfile.write("[singleuser#critical] " + msg.format(**kwargs) + "\n")

        # Be nice to Windows users who ran the program by double-clicking. :)
        if self._waitoncritical:
            input("Press Enter Key to Continue...")

    def write(self, msg):
        """Write an untagged message to the console and/or the log file, regardless of log level.
        """
        print(msg)
        self._logfile.write(str(msg) + "\n")


def main():
    print("Welcome to Dennis MUD {0}, Single User Mode.".format(VERSION))
    print("Starting up...")

    # When this is False, Dennis will shut down.
    _running = True

    # Try to open the singleuser config file.
    try:
        with open("singleuser.config.json") as f:
            config = json.load(f)
    except (OSError, IOError):
        print("[singleuser#critical] Could not open singleuser config file: singleuser.config.json")
        print(traceback.format_exc(1))
        return 2
    except json.JSONDecodeError:
        print("[server#critical] JSON error from singleuser config file: singleuser.config.json")
        print(traceback.format_exc(1))
        return 2

    # Try to open the log file for writing, if one is set.
    # Otherwise don't use one.
    if config["log"]["level"] in ["debug", "info"]:
        print("[singleuser#info] Initializing logger...")
    logfile = None
    if config["log"]["file"]:
        try:
            logfile = open(config["log"]["file"], 'a')
        except:
            if config["log"]["level"] in ["debug", "info", "warn"]:
                print("[singleuser#warn] Could not open singleuser log file: {0}".format(config["log"]["file"]))
                print(traceback.format_exc(1))
    log = Log(config["log"]["level"], logfile, config["log"]["wait_on_critical"])
    log.info("Finished initializing logger.")

    # Rotate database backups, if enabled.
    # Unfortunately this has to be done before loading the database, because Windows.
    if os.path.exists(config["database"]["filename"]):
        try:
            if config["database"]["backups"]:
                backupnumbers = sorted(range(1, config["database"]["backups"]), reverse=True)
                for bn in backupnumbers:
                    if os.path.exists("{0}.bk{1}".format(config["database"]["filename"], bn)):
                        shutil.copyfile("{0}.bk{1}".format(config["database"]["filename"], bn),
                                        "{0}.bk{1}".format(config["database"]["filename"], bn + 1))
                shutil.copyfile(config["database"]["filename"], "{0}.bk1".format(config["database"]["filename"]))
        except:
            log.error("Could not finish rotating backups for database: {0}".format(config["database"]["filename"]))
            log.error(traceback.format_exc(1))

    # Initialize the database manager, and create the "database" alias for use in Debug Mode.
    log.info("Initializing database manager...")
    dbman = _database.DatabaseManager(config["database"]["filename"], log)
    if not dbman._startup():
        return 3
    log.info("Finished initializing database manager.")
    database = dbman

    # Initialize the router.
    router = Router(log)

    # Initialize the command shell, and create the "shell" alias for use in Debug Mode.
    command_shell = _shell.Shell(dbman, router)
    router.shell = command_shell
    shell = command_shell

    # Initialize the command console, and log in as the root user. Promote to wizard if it was somehow demoted.
    # Create the "console" alias for use in Debug Mode. Also add us to the current room.
    dennis = _console.Console(router, command_shell, "<world>", dbman, log)
    dennis.user = dbman.user_by_name("<world>")
    dbman._users_online.append("<world>")
    thisroom = dbman.room_by_id(dennis.user["room"])
    if thisroom and "<world>" not in thisroom["users"]:
        thisroom["users"].append("<world>")
        dbman.upsert_room(thisroom)
    if not dennis.user["wizard"]:
        dennis.user["wizard"] = True
        dbman.upsert_user(dennis.user)
    console = dennis

    # Register our console with the router.
    router.users["<world>"] = {"service": "singleuser", "console": dennis}

    # Try to start a command prompt session with a history file.
    # Otherwise start a sessionless prompt without history.
    try:
        command_prompt = PromptSession(history=FileHistory(config["prompt"]["history"])).prompt
    except:
        log.error("Could not open prompt history file: {0}".format(config["prompt"]["history"]))
        log.error(traceback.format_exc(1))
        command_prompt = prompt

    # Stop Dennis. We use this instead of just a variable so that Dennis can be stopped from within a Python file
    # executed by load() in debug mode.
    def shutdown():
        """Stop Dennis."""
        nonlocal _running
        _running = False

    # Insert a simplified wrapper around dennis.shell.call() here so that it can access the current console
    # without us having to pass it as an argument.
    def call(command, args):
        """Simplified wrapper around dennis.shell.call().

        This shorthand function allows calling a command from Debug Mode
        without having to pass the current console as an argument.
        It can also take either a list or a string for args.

        :param command: The name of the command to call.
        :param args: A list or string of args to pass.

        :return: True if succeeded, False if failed.
        """
        if type(args) is str:
            args = args.split(' ')
        return dennis.shell.call(dennis, command, args)

    # Save the main scope for load().
    mainscope = locals()

    # Insert a function for Debug Mode to load and execute a Python file inside the main scope.
    def load(filename):
        """Load and execute a Python file inside the main scope.

        This is the same as running a series of lines in Debug mode.
        It can be called as a function from Debug mode, or as a command.

        Usage: `load <filename>`.

        :param filename: The filename of the Python file to execute.

        :return: True if succeeded, False if failed.
        """
        # Try to evaluate the given file.
        try:
            file = open(filename)
        except:
            log.write("[singleuser#error] load: Failed to load Python file: {0}".format(filename))
            log.write(traceback.format_exc(1))
            return False
        try:
            exec(file.read(), globals(), mainscope)
        except:
            log.write("[singleuser#error] load: Execution error inside file: {0}".format(filename))
            log.write(traceback.format_exc(1))
            return False
        return True

    # Welcome!
    log.write("You are now logged in as the administrative user \"<world>\".")

    # # # # # # # # # #
    # This is the command loop for the Single User Mode Command Line Interface. It works almost the same as connecting
    # to a Multi User server through Telnet, with a few differences:
    # * The return status of commands will echo in the console.
    # * You play as the system administrator user <world>, who is always a wizard, and owns the first room.
    # * Other users can't share the session with you.
    # * You have access to the following special commands:
    #   - `quit`             : Quits the CLI.
    #   - `debug`            : Enters a PDB Debug Mode session inside the main scope.
    #   - `load <filename>`  : Loads and executes an external Python file inside the main scope.
    #
    # * You have access to the following special functions inside Debug Mode:
    #   - shutdown()          : Cleanly shuts down the engine.
    #   - call(command, args) : Calls the named command with a string or list of arguments.
    #   - load(filename)      : Same as the `load <filename>` command.
    #
    # * You have access to the following special keypress actions:
    #   - Ctrl+C              : Cleanly shuts down the engine.
    #   - Ctrl+D              : Enters a PDB Debug Mode session inside the main scope.
    #
    # * You can return from Debug Mode to normal operation by entering "continue".
    # # # # # # # # # #
    while _running:
        try:
            cmd = command_prompt("> ")
            if cmd == "quit":
                break
            elif cmd.startswith("quit ") or cmd == "help quit":
                log.write("Usage: quit")
                continue
            elif cmd == "debug":
                pdb.set_trace()
                continue
            elif cmd.startswith("debug ") or cmd == "help debug":
                log.write("Usage: debug")
                continue
            elif cmd.startswith("load "):
                log.write(load(cmd[5:]))
                continue
            elif cmd == "load" or cmd == "help load":
                log.write("Usage: load <filename>")
                continue
            log.write(command_shell.command(dennis, cmd))
        except KeyboardInterrupt:
            break
        except EOFError:
            pdb.set_trace()
            continue

    # Just before shutdown.
    dbman._unlock()
    log.write("End Program.")
    return 0


# Don't do anything if we're not running as a program.
# Otherwise, run main() and return its exit status to the OS.
# Return Codes:
# * 0: Success.
# * 1: Wrong Python version.
# * 2: Could not read main configuration file.
# * 3: Could not initialize DatabaseManager.
if __name__ == "__main__":
    sys.exit(main())
