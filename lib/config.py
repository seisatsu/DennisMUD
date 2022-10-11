##################
# Dennis MUD     #
# config.py      #
# Copyright 2020 #
# Sei Satzparad  #
##################

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

# This code adapted from Driftwood 2D Game Dev. Suite,
# Copyright 2014-2017 Sei Satzparad     and Paul Merrill.
# https://github.com/Driftwood2D/Driftwood

import argparse
import json
import jsonschema
import os
import sys
import traceback

from lib.logger import timestamp

VERSION = "Dennis MUD v0.0.3-Alpha"
COPYRIGHT = "Copyright 2018-2022 Sei Satzparad"


class ConfigManager:
    """The Config Manager

    This class reads command line input and a configuration file and presents the resulting configuration for easy
    access. Command line options always supersede their configuration file equivalents.
    
    :ivar config: The internal dictionary of all config values. Base keys are "defaults", "server", and "singleuser".
    :ivar defaults: A convenience class instance providing protected access to just the defaults config values.
    :ivar vars: A convenience class instance providing protected access to special command-line-only variables.
    """

    def __init__(self, single):
        """ConfigManager class initializer.

        :param single: Whether or not to run in single user mode.
        """
        # This is a ConfigBaseKey pseudo-dictionary of server or singleuser config values.
        self.config = ConfigBaseKey()

        # This is a ConfigBaseKey pseudo-dictionary of defaults config values.
        self.defaults = None

        # Here we allow special command-line-only config variables.
        # They are passed on the command line in Quake style: +varname=value
        self.vars = ConfigBaseKey()

        # This is empty at the start when the Logger hasn't been initialized yet.
        self._log = None

        # Run initialization steps. It's ok to do an unclean sys.exit() during these because
        # we are just starting up the engine.
        self._single = single
        self._read_cmdline_vars()
        self._cmdline_args = self._read_cmdline()
        self._prepare_config()

    def __contains__(self, item):
        if item in self.config:
            return True
        return False

    def __getitem__(self, item):
        if self.__contains__(item):
            return self.config[item]
        else:
            # Config variables should never be null, so this works as an unambiguous error code.
            return None

    def __setitem__(self, key, value):
        self.config[key] = value

    def __iter__(self):
        return iter(self.config.__iter__())

    def _read_cmdline_vars(self):
        """Read command line engine variable assignments first.

        These need to get out of the way before we use Argparse, which can't handle them.

        :returns: None
        """
        for item in sys.argv[1:]:
            if item[0] == '+':
                # Remove this so it doesn't bother Argparse later.
                sys.argv.remove(item)
                assignment = item[1:].split('=')
                # There should only be one = sign in an engine variable assignment. Fail.
                if len(assignment) != 2:
                    print("{0} [config#critical] Invalid variable assignment on command line: {1}".format(
                        timestamp(), item))
                    sys.exit(2)
                self.vars[assignment[0]] = assignment[1]

    def _read_cmdline(self) -> argparse.Namespace:
        """Read in command line options using ArgumentParser.

        :returns: Result of parser.parse_args().
        """
        parser = argparse.ArgumentParser(
            description=VERSION + (", Single User Mode" if self._single else ", Multi-Player Server"),
                                         formatter_class=lambda prog: argparse.HelpFormatter(prog,
                                                                                             max_help_position=40))

        # These arguments are always available.
        parser.add_argument("--defaults-config", nargs=1, dest="defaultsfile", type=str, metavar="<filename>",
                            default=["defaults.config.json"], help="alternate defaults config file to use")
        parser.add_argument("--db", nargs=1, dest="db", type=str, metavar="<filename>",
                            help="database file to use")
        parser.add_argument("--backups", nargs=1, dest="backups", type=int, metavar="<number>",
                            help="maximum number of backups to keep")
        parser.add_argument("--log-file", nargs=1, dest="logfile", type=str, metavar="<filename>",
                            help="log file to use")
        parser.add_argument("--log-level", nargs=1, dest="loglevel", type=str, metavar="<level>",
                            help="log level to use")
        parser.add_argument("--help-columns", nargs=1, dest="helpcolumns", type=int, metavar="<number>",
                            help="number of columns to use for formatting help lists")

        # These arguments are available in Single User Mode.
        if self._single:
            parser.add_argument("--singleuser-config", nargs=1, dest="singleuserfile", type=str, metavar="<filename>",
                                default=["singleuser.config.json"], help="alternate singleuser config file to use")
            parser.add_argument("--wait-on-critical", nargs=1, dest="waitoncritical", type=str, metavar="<1|0>",
                                help="whether to wait before exiting on critical errors")
            parser.add_argument("--history-file", nargs=1, dest="historyfile", type=str, metavar="<filename>",
                                help="command prompt history file to use")

        # These arguments are available in Multi-Player Mode.
        else:
            parser.add_argument("--server-config", nargs=1, dest="serverfile", type=str, metavar="<filename>",
                                default=["server.config.json"], help="alternate server config file to use")
            parser.add_argument("--log-stdout", nargs=1, dest="stdout", type=str, metavar="<1|0>",
                                help="whether to log to stdout")
            parser.add_argument("--telnet-port", nargs=1, dest="telnetport", type=int, metavar="<port>",
                                help="telnet port to use, 0 to disable")
            parser.add_argument("--websocket-port", nargs=1, dest="websocketport", type=int, metavar="<port>",
                                help="websocket port to use, 0 to disable")
            parser.add_argument("--websocket-host", nargs=1, dest="websockethost", type=str, metavar="<hostname>",
                                help="websocket hostname to use")
            parser.add_argument("--websocket-secure", nargs=1, dest="websocketsecure", type=str, metavar="<1|0>",
                                help="whether to use secure websockets")
            parser.add_argument("--websocket-key", nargs=1, dest="websocketkey", type=str, metavar="<filename>",
                                help="websocket key file to use")
            parser.add_argument("--websocket-cert", nargs=1, dest="websocketcert", type=str, metavar="<filename>",
                                help="websocket certificate file to use")
            parser.add_argument("--shutdown-delay", nargs=1, dest="shutdowndelay", type=int, metavar="<seconds>",
                                help="shutdown delay in seconds")
            parser.add_argument("--disable-commands", nargs=1, dest="disablecommands", type=int,
                                metavar="<command,...>", help="comma separated list of commands to disable")

        # The version argument returns version and copyright info and exits.
        parser.add_argument("--version", action="store_true", dest="version", help="print the version string")

        # Finished.
        return parser.parse_args()

    def _prepare_config(self):
        """Prepare the configuration for use.

        Combine the command line arguments and the configuration files into the ConfigBaseClass pseudo-dictionaries,
        favoring command line arguments. Also validate the configuration files using JSON schemas.
        """
        # If --version was used, print the version string and exit.
        if self._cmdline_args.version:
            print(VERSION + (", Single User Mode" if self._single else ", Multi-Player Server"))
            print(COPYRIGHT)
            sys.exit(0)

        # Variables for loading configuration schemas.
        schemadir = os.getcwd() + "/lib/schema/"
        schema = {}

        # Load the defaults configuration schema, otherwise fail.
        try:
            with open("{0}{1}".format(schemadir, "defaults.json")) as schemafile:
                schema["defaults"] = json.load(schemafile)
        except (OSError, IOError):
            print("{0} [config#critical] Could not open defaults schema file: {1}".format(
                timestamp(), "{0}{1}".format(schemadir, "defaults.json")))
            print(traceback.format_exc(1))
            sys.exit(2)
        except json.JSONDecodeError:
            print("{0} [config#critical] JSON error from defaults schema file: {1}".format(
                timestamp(), "{0}{1}".format(schemadir, "defaults.json")))
            print(traceback.format_exc(1))
            sys.exit(2)

        # If single user mode, load the singleuser configuration schema, otherwise fail.
        if self._single:
            try:
                with open("{0}{1}".format(schemadir, "singleuser.json")) as schemafile:
                    schema["singleuser"] = json.load(schemafile)
            except (OSError, IOError):
                print("{0} [config#critical] Could not open singleuser schema file: {1}".format(
                    timestamp(), "{0}{1}".format(schemadir, "singleuser.json")))
                print(traceback.format_exc(1))
                sys.exit(2)
            except json.JSONDecodeError:
                print("{0} [config#critical] JSON error from singleuser schema file: {1}".format(
                    timestamp(), "{0}{1}".format(schemadir, "singleuser.json")))
                print(traceback.format_exc(1))
                sys.exit(2)

        # If server mode, load the server configuration schema, otherwise fail.
        else:
            try:
                with open("{0}{1}".format(schemadir, "server.json")) as schemafile:
                    schema["server"] = json.load(schemafile)
            except (OSError, IOError):
                print("{0} [config#critical] Could not open server schema file: {1}".format(
                    timestamp(), "{0}{1}".format(schemadir, "server.json")))
                print(traceback.format_exc(1))
                sys.exit(2)
            except json.JSONDecodeError:
                print("{0} [config#critical] JSON error from server schema file: {1}".format(
                    timestamp(), "{0}{1}".format(schemadir, "server.json")))
                print(traceback.format_exc(1))
                sys.exit(2)

        # Load the defaults configuration file and validate against the schema, otherwise fail.
        try:
            with open(self._cmdline_args.defaultsfile[0], 'r') as defaultsfile:
                self.defaults = ConfigBaseKey(json.load(defaultsfile))
                jsonschema.validate(self.defaults.config, schema["defaults"])
                self.config["defaults"] = self.defaults
        except (OSError, IOError):
            print("{0} [config#critical] Could not open defaults config file: {1}".format(
                timestamp(), self._cmdline_args.defaultsfile[0]))
            print(traceback.format_exc(1))
            sys.exit(2)
        except json.JSONDecodeError:
            print("{0} [config#critical] JSON error from defaults config file: {1}".format(
                timestamp(), self._cmdline_args.defaultsfile[0]))
            print(traceback.format_exc(1))
            sys.exit(2)
        except jsonschema.ValidationError:
            print("{0} [config#critical] JSON schema validation error from defaults config file: {1}".format(
                timestamp(), self._cmdline_args.defaultsfile[0]))
            print(traceback.format_exc(1))
            sys.exit(2)

        # If single user mode, load the singleuser configuration file, otherwise fail.
        if self._single:
            try:
                with open(self._cmdline_args.singleuserfile[0], 'r') as singleuserfile:
                    self.config = ConfigBaseKey(json.load(singleuserfile))
                    jsonschema.validate(self.config.config, schema["singleuser"])
            except (OSError, IOError):
                print("{0} [config#critical] Could not open singleuser config file: {1}".format(
                    timestamp(), self._cmdline_args.singleuserfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)
            except json.JSONDecodeError:
                print("{0} [config#critical] JSON error from singleuser config file: {1}".format(
                    timestamp(), self._cmdline_args.singleuserfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)
            except jsonschema.ValidationError:
                print("{0} [config#critical] JSON schema validation error from singleuser config file: {1}".format(
                    timestamp(), self._cmdline_args.singleuserfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)

        # If server mode, load the server configuration file, otherwise fail.
        else:
            try:
                with open(self._cmdline_args.serverfile[0], 'r') as serverfile:
                    self.config = ConfigBaseKey(json.load(serverfile))
                    jsonschema.validate(self.config.config, schema["server"])
            except (OSError, IOError):
                print("{0} [config#critical] Could not open server config file: {1}".format(
                    timestamp(), self._cmdline_args.serverfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)
            except json.JSONDecodeError:
                print("{0} [config#critical] JSON error from server config file: {1}".format(
                    timestamp(), self._cmdline_args.serverfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)
            except jsonschema.ValidationError:
                print("{0} [config#critical] JSON schema validation error from server config file: {1}".format(
                    timestamp(), self._cmdline_args.serverfile[0]))
                print(traceback.format_exc(1))
                sys.exit(2)

        # Parse command line options that are available in both modes.
        if self._cmdline_args.db:
            self.config["database"]["filename"] = self._cmdline_args.db[0]
        if self._cmdline_args.backups:
            self.config["database"]["backups"] = self._cmdline_args.backups[0]
        if self._cmdline_args.logfile:
            self.config["log"]["file"] = self._cmdline_args.logfile[0]
        if self._cmdline_args.loglevel:
            self.config["log"]["level"] = self._cmdline_args.loglevel[0]
        if self._cmdline_args.helpcolumns:
            self.config["defaults"]["help"]["columns"] = self._cmdline_args.helpcolumns[0]

        # Parse command line options that are available in single user mode.
        if self._single:
            if self._cmdline_args.waitoncritical:
                if self._cmdline_args.waitoncritical[0].lower() in ["1", "on", "true", "enable", "enabled", "yes"]:
                    self.config["log"]["wait_on_critical"] = True
                else:
                    self.config["log"]["wait_on_critical"] = False
            if self._cmdline_args.historyfile:
                self.config["prompt"]["history"] = self._cmdline_args.historyfile[0]

        # Parse command line options that are available in server mode.
        else:
            if self._cmdline_args.stdout:
                if self._cmdline_args.stdout[0].lower() in ["1", "on", "true", "enable", "enabled", "yes"]:
                    self.config["log"]["stdout"] = True
                else:
                    self.config["log"]["stdout"] = False
            if self._cmdline_args.telnetport:
                if self._cmdline_args.telnetport[0] == 0:
                    self.config["telnet"]["enabled"] = False
                else:
                    self.config["telnet"]["enabled"] = True
                    self.config["telnet"]["port"] = self._cmdline_args.telnetport[0]
            if self._cmdline_args.websocketport:
                if self._cmdline_args.websocketport[0] == 0:
                    self.config["websocket"]["enabled"] = False
                else:
                    self.config["websocket"]["enabled"] = True
                    self.config["websocket"]["port"] = self._cmdline_args.websocketport[0]
            if self._cmdline_args.websockethost:
                self.config["websocket"]["host"] = self._cmdline_args.websockethost[0]
            if self._cmdline_args.websocketsecure:
                if self._cmdline_args.websocketsecure[0].lower() in ["1", "on", "true", "enable", "enabled", "yes"]:
                    self.config["websocket"]["secure"] = True
                else:
                    self.config["websocket"]["secure"] = False
            if self._cmdline_args.websocketkey:
                self.config["websocket"]["key"] = self._cmdline_args.websocketkey[0]
            if self._cmdline_args.websocketcert:
                self.config["websocket"]["cert"] = self._cmdline_args.websocketcert[0]
            if self._cmdline_args.shutdowndelay:
                self.config["shutdown_delay"] = self._cmdline_args.shutdowndelay[0]
            if self._cmdline_args.disablecommands:
                self.config["disabled"] = self._cmdline_args.disablecommands[0].split(',')


class ConfigBaseKey:
    """This is a convenience class for providing protected access to just a section of the config.

    It behaves almost exactly like a dictionary, so you can basically treat it like one.
    The major difference is that it won't crash if you try to pull a nonexistent key.
    """
    def __init__(self, document=None):
        if document is None:
            self.config = {}
        else:
            self.config = document

    def __contains__(self, item):
        if item in self.config:
            return True
        return False

    def __getitem__(self, item):
        if self.__contains__(item):
            return self.config[item]
        else:
            return None

    def __setitem__(self, key, value):
        self.config[key] = value

    def __iter__(self):
        return iter(self.config.keys())
