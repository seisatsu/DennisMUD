#####################
# Dennis MUD        #
# chat.py           #
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

NAME = "chat"
CATEGORIES = ["messaging"]
SPECIAL_ALIASES = ['#']
USAGE = "chat <message>"
DESCRIPTION = """Send a message to the general chat.

General chat messages are seen by all online users who have chat enabled and are not ignoring you.
You must also have chat enabled to send a message.

Ex. `chat Hello everyone!`
Ex2. `#Hello everyone!`"""


def COMMAND(console, args):
    if len(args) < 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Make sure chat is enabled.
    if not console.user["chat"]["enabled"]:
        console.msg(NAME + ": enable chat first")
        return False

    for u in console.router.users:
        if console.router.users[u]["console"].user and console.router.users[u]["console"].user["chat"]["enabled"]:
            if not console.user["name"] in console.router.users[u]["console"].user["chat"]["ignored"]:
                console.router.users[u]["console"].msg("# <" + console.user["name"] + ">: " + ' '.join(args))

    return True
