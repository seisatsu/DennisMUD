#####################
# Dennis MUD        #
# rename_self.py    #
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

NAME = "rename self"
CATEGORIES = ["settings", "users"]
USAGE = "rename self <nickname>"
DESCRIPTION = """Set your player nickname to <nickname>.

Your nickname is separate from your username. People will see it instead of your username in most cases.

Ex. `rename self Overlord Seisatsu`"""


def COMMAND(console, database, args):
    if len(args) == 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Get name.
    name = ' '.join(args)

    # Make sure the name is not an integer, as this would be confusing.
    try:
        test = int(name)
        console.msg(NAME + ": nickname cannot be an integer")
        return False
    except ValueError:
        # Not an integer.
        pass

    # Check if nickname is already in use.
    for u in database.users.all():
        if name.lower() == u["nick"].lower():
            console.msg(NAME + ": that nickname is already in use")
            return False

    console.user["nick"] = name
    database.upsert_user(console.user)
    console.msg(NAME + ": done")
    return True
