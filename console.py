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

from twisted.logger import Logger


class Console:
    """Console

    Each instance of the console corresponds to a single user session. The console abstracts interaction between a user
    and the router and shell.

    :ivar user: TinyDB user document for the currently logged in user, if any.
    :ivar router: The Router instance, which handles interfacing between the server backend and the user consoles.
    :ivar shell: The shell instance, which handles commands and help.
    :ivar rname: The name used by the router for this console.
    :ivar shell: The Shell instance, which handles commands and help, and communication with the router.
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
        self.router = router
        self.shell = shell
        self.rname = rname
        self._database = database
        self._log = log or Logger("console:{0}".format(rname))

        self._commands = {}
        self._help = {}
        self._special_aliases = {}
        self._disabled_commands = []

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
