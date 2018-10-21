#####################
# Dennis MUD        #
# message.py        #
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

NAME = "message"
CATEGORIES = ["messaging"]
USAGE = "message <username> <message>"
DESCRIPTION = """Send a message to the user <username>. Does not use nicknames. Aliases: msg and .

If you don't know a player's username, you can look it up using their nickname with the `realname` command.

Ex. `message seisatsu Hello there!`
Ex2. `msg seisatsu Hello there!`
Ex3. `.seisatsu Hello there!`"""


def COMMAND(console, database, args):
    if len(args) < 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    for u in console.router.users:
        if console.router.users[u].user and console.router.users[u].user["name"] == args[0].lower():
            if not console.user["name"] in console.router.users[u].user["chat"]["ignored"] or console.user["wizard"]:
                console.router.users[u].msg("<<" + console.user["name"] + ">>: " + ' '.join(args[1:]))
                console.msg("<<" + console.user["name"] + ">>: " + ' '.join(args[1:]))
            return True

    console.msg(NAME + ": no such user is logged in")
    return False
