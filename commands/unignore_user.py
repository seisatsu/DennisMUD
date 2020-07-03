#####################
# Dennis MUD        #
# unignore_user.py  #
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

NAME = "unignore user"
CATEGORIES = ["messaging", "settings", "users"]
USAGE = "unignore user <username>"
DESCRIPTION = """Unignore general chat messages and private messages from the user <username>.

Undoes ignoring a user via the `ignore user` command.

Ex. `unignore user seisatsu`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Lookup target user.
    targetuser = COMMON.check_user(NAME, console, args[0].lower())
    if not targetuser:
        return False

    # Check if user is already not ignored.
    if targetuser["name"] not in console.user["chat"]["ignored"]:
        console.msg("{0}: already not ignoring user".format(NAME))
        return False

    # Ignore the user.
    console.user["chat"]["ignored"].remove(targetuser["name"])
    console.database.upsert_user(console.user)

    # Finished.
    console.msg("{0}: done".format(NAME))
    return True
