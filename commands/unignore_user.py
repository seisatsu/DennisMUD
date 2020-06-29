#####################
# Dennis MUD        #
# unignore_user.py  #
# Copyright 2019    #
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

NAME = "unignore user"
CATEGORIES = ["messaging", "settings", "users"]
USAGE = "unignore user <username>"
DESCRIPTION = """Unignore general chat messages and private messages from the user <username>.

Undoes ignoring a user via the `ignore user` command.

Ex. `unignore user seisatsu`"""


def COMMAND(console, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Lookup user.
    targetuser = console.database.user_by_name(args[0])
    if not targetuser:
        # No such user.
        console.msg(NAME + ": no such user")
        return False

    # Check if user is already not ignored.
    if targetuser["name"] not in console.user["chat"]["ignored"]:
        console.msg(NAME + ": already not ignoring user")
        return False

    console.user["chat"]["ignored"].remove(targetuser["name"])
    console.database.upsert_user(console.user)

    console.msg(NAME + ": done")
    return True
