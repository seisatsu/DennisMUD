#######################
# Dennis MUD          #
# console.py          #
# Copyright 2018-2020 #
# Michael D. Reiley   #
#######################

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

from lib.logger import Logger


class Console:
    """Console

    Each instance of the console corresponds to a single user session. The console abstracts interaction between a user
    and the router and shell.

    :ivar user: The TinyDB user document for the currently logged in user, if any.
    :ivar vars: A dict of temporary variables that will disappear on shutdown.
    :ivar router: The Router instance, which handles interfacing between the server backend and the user consoles.
    :ivar shell: The shell instance, which handles commands and help.
    :ivar rname: The name used by the router for this console.
    :ivar shell: The Shell instance, which handles commands and help, and communication with the router.
    :ivar database: The DatabaseManager instance.
    :ivar log: The Logger for this console.
    :ivar exits: The list of exit names in the current room, if any.
    """
    def __init__(self, router, shell, rname, database, log=None):
        """Console Initializer

        :param router: The Router instance, which handles interfacing between the server backend and the user consoles.
        :param shell: The shell instance, which handles commands and help.
        :param rname: The name used by the router for this console.
        :param database: The DatabaseManager instance to use.
        :param log: Alternative logging facility, if not set.
        """
        self.user = None
        self.vars = {}
        self.router = router
        self.shell = shell
        self.rname = rname
        self.database = database
        self.log = log or Logger("console:{0}".format(rname))
        self.exits = []

        self._commands = {}
        self._help = {}
        self._special_aliases = {}
        self._disabled_commands = []
        self._login_delay = False

    def __contains__(self, item):
        """__contains__

        Check if a console variable exists.

        :param item: Console variable name.

        :return: True if succeeded, False if failed.
        """
        if item in self.vars:
            return True
        return False

    def __getitem__(self, item):
        """__getitem__

        Get a console variable by its name.

        :param item: Console variable name.

        :return: Console variable if succeeded, None if failed.
        """
        if self.__contains__(item):
            return self.vars[item]
        else:
            return None

    def __setitem__(self, item, value):
        """__setitem__

        Assign a value to a console variable.

        :param item: Console variable name.
        :param value: New value.

        :return: True
        """
        self.vars[item] = value
        return True

    def msg(self, message, _nbsp=False):
        """Send Message

        Send a message to the user connected to this console.

        :param message: The message to send.
        :param _nbsp: Will insert non-breakable spaces for formatting on the websocket frontend.

        :return: True
        """
        if self.router.single_user:
            self.log.write(message)
        else:
            self.log.info(message)
        self.router.message(self.rname, message, _nbsp)
        return True

    def _reset_login_delay(self):
        """Set self._login_delay to False.
        """
        self._login_delay = False
