#####################
# Dennis MUD        #
# message.py        #
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

NAME = "message"
CATEGORIES = ["messaging"]
ALIASES = ["msg", "tell"]
USAGE = "message <username> <message>"
DESCRIPTION = """Send a message to the user <username>. Does not use nicknames.

If you don't know a player's username, you can look it up using their nickname with the `realname` command.

Ex. `message seisatsu Hello there!`
Ex2. `msg seisatsu Hello there!`
Ex3. `.seisatsu Hello there!`"""


def COMMAND(console, args):
    if len(args) < 2:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Make sure the target user exists and is online, and get their record.
    targetuser = console.shell.user_by_name(args[0].lower())
    if not targetuser or not console.database.online(args[0].lower()):
        console.msg(NAME + ": no such user is logged in")
        return False

    # Message the user if we are a wizard or not ignored.
    if console.user["wizard"] or not console.user["name"] in targetuser["chat"]["ignored"]:
            console.shell.msg_user(args[0].lower(), "<<" + console.user["name"] + ">>: " + ' '.join(args[1:]))
            console.msg("<<" + console.user["name"] + ">>: " + ' '.join(args[1:]))
            return True

    # We are probably ignored.
    console.msg(NAME + ": could not message user")
    return False
