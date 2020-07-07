#####################
# Dennis MUD        #
# rename_self.py    #
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

NAME = "rename self"
CATEGORIES = ["settings", "users"]
USAGE = "rename self <nickname>"
DESCRIPTION = """Set your player nickname to <nickname>.

Your nickname is separate from your username. People will see it instead of your username in most cases.

Ex. `rename self Overlord Seisatsu`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Make sure the name is not an integer, as this would be confusing.
    # We actually want an exception to be raised here.
    if len(args) == 1:
        try:
            int(args[0])
            console.msg("{0}: Your nickname cannot be an integer.".format(NAME))
            return False
        except ValueError:
            # Not an integer.
            pass

    # Get new nickname.
    nickname = ' '.join(args)
    if nickname == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Make sure a user with this nickname does not already exist.
    # Make an exception if that user is us. (changing case)
    if console.database.user_by_nick(nickname) and nickname.lower() != console.user["nick"].lower():
        console.msg("{0}: That nickname is already in use.".format(NAME))
        return False

    # Rename ourselves.
    console.user["nick"] = nickname
    console.database.upsert_user(console.user)

    # Finished.
    console.msg("{0}: Done.")
    return True
