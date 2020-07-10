#####################
# Dennis MUD        #
# shutdown.py       #
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

import os
import signal
import time

NAME = "shutdown"
CATEGORIES = ["wizard"]
USAGE = "shutdown [seconds]"
DESCRIPTION = "(WIZARDS ONLY) Shut down the server, with optional seconds argument."


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=0, argmax=1, wizard=True):
        return False

    # Make sure we are not already shutting down.
    if console.router.shutting_down:
        console.msg("{0}: Already shutting down.".format(NAME))
        return False

    # Take seconds argument if given. Otherwise use the default.
    if len(args) == 1:
        # Perform argument type checks and casts.
        seconds = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
        if seconds is None:
            return False
    else:
        seconds = console.router._config["shutdown_delay"]

    # Gracefully shut down in multi-user mode, or else send ourselves the TERM signal.
    if hasattr(console.router, "_reactor"):
        console.shell.broadcast("<<<DENNIS IS SHUTTING DOWN IN {0} SECONDS>>>".format(seconds))
        console.router._reactor.callLater(seconds, console.router._reactor.stop)
        console.router.shutting_down = True
    else:
        os.kill(os.getpid(), signal.SIGTERM)
