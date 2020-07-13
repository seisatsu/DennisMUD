#######################
# Dennis MUD          #
# message.py          #
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

NAME = "message"
CATEGORIES = ["messaging"]
ALIASES = ["msg", "tell"]
SPECIAL_ALIASES = ['.']
USAGE = "message <username> <message>"
DESCRIPTION = """Send a private message to the user <username>. Does not use nicknames.

If you don't know a player's username, you can look it up using their nickname with the `realname` command.
To ignore a particular user's private messages, you may use the `ignore user` command.

Ex. `message seisatsu Hello there!`
Ex2. `msg seisatsu Hello there!`
Ex3. `.seisatsu Hello there!`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2):
        return False

    # Make sure the named user exists and is online.
    targetuser = COMMON.check_user(NAME, console, args[0].lower(), online=True)
    if not targetuser:
        return False

    # Make sure we are not ignored or we are a wizard.
    if console.user["name"] in targetuser["chat"]["ignored"] and not console.user["wizard"]:
        console.msg("{0}: Could not message user.".format(NAME))
        return False

    # Finished. Message the user, and echo the message to ourselves, if it wasn't a self-message.
    console.shell.msg_user(args[0].lower(), "<<{0}>>: {1}".format(console.user["name"], ' '.join(args[1:])))
    if targetuser["name"] != console.user["name"]:
        console.msg("<<{0}>>: {1}".format(console.user["name"], ' '.join(args[1:])))
    return True

