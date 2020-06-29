#####################
# Dennis MUD        #
# action.py         #
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

NAME = "action"
CATEGORIES = ["messaging"]
ALIASES = ["emote", "me"]
SPECIAL_ALIASES = [':']
USAGE = "action <message>"
DESCRIPTION = """Send a message styled as performing an action.

By default, the action text is shown following your nickname and one space.
To place your name elsewhere in the text, use the %player% marker.

Ex. `action trips and falls over.`
Ex2. `action A coconut falls on %player%'s head.`
Ex3. `me trips and falls over.`
Ex4. `:trips and falls over.`"""


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Construct and broadcast the action text.
    action = ' '.join(args)
    if "%player%" in action:
        action = action.replace("%player%", console.user["nick"])
    else:
        action = console.user["nick"] + " " + ' '.join(args)
    console.shell.broadcast_room(console, action)

    return True
