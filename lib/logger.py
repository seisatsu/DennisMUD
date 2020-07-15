#####################
# Dennis MUD        #
# logger.py         #
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

import datetime
import time
import traceback

# Variables shared between all Logger instances.
_LOGFILE = None
_LOGLEVEL = None
_STDOUT = None
_WAITONCRITICAL = None


def init(config):
    """Initialize the Logger system.
    
    This must be run before creating any Logger instances.
    It sets up global variables that are shared between all Loggers.
    """
    global _LOGFILE, _LOGLEVEL, _STDOUT, _WAITONCRITICAL

    # Note that we are initializing the logger.
    print("Initializing logger...")

    # On singleuser, we might wait on critical errors.
    if "wait_on_critical" in config["log"]:
        _WAITONCRITICAL = config["log"]["wait_on_critical"]

    # Make sure the chosen log level is valid. Otherwise force the highest log level.
    if config["log"]["level"] not in ["critical", "error", "warn", "info", "debug"]:
        print(timestamp(), "[logger#error] Invalid log level in config, defaulting to \"debug\".")
        config["log"]["level"] = "debug"
    _LOGLEVEL = config["log"]["level"]

    # For the server, give an error if no logging option is selected, and default to stdout.
    # On singleuser, stdout is always enabled.
    if "stdout" in config["log"]:
        if not config["log"]["stdout"] and not config["log"]["file"]:
            # No logging target is set, so force stdout.
            print(timestamp(), "[logger#error] No logging target in config, defaulting to stdout.")
            config["log"]["stdout"] = True
            _STDOUT = True
        elif config["log"]["stdout"]:
            _STDOUT = True
    else:
        _STDOUT = True

    # Try to open the log file. If this fails, give an error and default to stdout.
    if config["log"]["file"]:
        try:
            _LOGFILE = open(config["log"]["file"], 'a')
        except:
            if _LOGLEVEL in ["debug", "info", "warn", "error"]:
                print(timestamp(), "[logger#error] Could not open log file: {0}".format(
                    config["log"]["file"]))
                print(traceback.format_exc(1))
            if "stdout" in config["log"]:
                config["log"]["stdout"] = True
                _STDOUT = True

    # Note that we have finished initializing the logger.
    if _LOGLEVEL in ["debug", "info"]:
        if _STDOUT:
            print(timestamp(), "[logger#info] Finished initializing logger.")
        if _LOGFILE:
            _LOGFILE.write(timestamp() + " [logger#info] Finished initializing logger.\n")


def timestamp():
    """Return a Log timestamp.

    :return: Timestamp string.
    """
    # Thanks to https://stackoverflow.com/questions/3168096/getting-computers-utc-offset-in-python
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    utc_offset = - (time.altzone if is_dst else time.timezone)
    return "{0}{1}".format(datetime.datetime.now().isoformat(), str(int(utc_offset / 3.6)))


class Logger:
    """Logger.

    Logs to STDOUT, and optionally to a file, and filters unwanted messages based on a log level setting.
    Each Logger instance can have its own namespace for which it tags messages.
    """
    def __init__(self, namespace):
        """Logger Initializer.

        :param namespace: The name of the subsystem this Logger instance is logging for.
        """
        self._namespace = namespace

    def debug(self, msg, **kwargs):
        """Write a debug level message to the console and/or the log file.
        """
        if _LOGLEVEL in ["debug"]:
            if _STDOUT:
                print("{0} [{1}#debug] {2}".format(timestamp(), self._namespace, msg.format(**kwargs)))
            if _LOGFILE:
                _LOGFILE.write("{0} [{1}#debug] {2}\n".format(timestamp(), self._namespace, msg.format(**kwargs)))

    def info(self, msg, **kwargs):
        """Write an info level message to the console and/or the log file.
        """
        if _LOGLEVEL in ["debug", "info"]:
            if _STDOUT:
                print("{0} [{1}#info] {2}".format(timestamp(), self._namespace, msg.format(**kwargs)))
            if _LOGFILE:
                _LOGFILE.write("{0} [{1}#info] {2}\n".format(timestamp(), self._namespace, msg.format(**kwargs)))

    def warn(self, msg, **kwargs):
        """Write a warn level message to the console and/or the log file.
        """
        if _LOGLEVEL in ["debug", "info", "warn"]:
            if _STDOUT:
                print("{0} [{1}#warn] {2}".format(timestamp(), self._namespace, msg.format(**kwargs)))
            if _LOGFILE:
                _LOGFILE.write("{0} [{1}#warn] {2}\n".format(timestamp(), self._namespace, msg.format(**kwargs)))

    def error(self, msg, **kwargs):
        """Write an error level message to the console and/or the log file.
        """
        if _LOGLEVEL in ["debug", "info", "warn", "error"]:
            if _STDOUT:
                print("{0} [{1}#error] {2}".format(timestamp(), self._namespace, msg.format(**kwargs)))
            if _LOGFILE:
                _LOGFILE.write("{0} [{1}#error] {2}\n".format(timestamp(), self._namespace, msg.format(**kwargs)))

    def critical(self, msg, **kwargs):
        """Write a critical level message to the console and/or the log file.

        All log levels include critical, so these messages cannot be disabled.
        """
        print("{0} [{1}#critical] {2}".format(timestamp(), self._namespace, msg.format(**kwargs)))
        if _LOGFILE:
            _LOGFILE.write("{0} [{1}#critical] {2}\n".format(timestamp(), self._namespace, msg.format(**kwargs)))

        # Be nice to Windows users who ran the program by double-clicking. :)
        if _WAITONCRITICAL:
            input("Press Enter Key to Continue...")

    def write(self, msg):
        """Write an untagged message to the console and/or the log file, regardless of log level.
        """
        print(msg)
        if _LOGFILE:
            _LOGFILE.write("{0} {1}\n".format(timestamp(), msg))
