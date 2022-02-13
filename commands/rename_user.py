#######################
# Dennis MUD          #
# rename_user.py      #
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

NAME = "rename user"
CATEGORIES = ["wizards"]
USAGE = "rename user <name> <nickname>"
DESCRIPTION = """Set a target player's nickname to <nickname>.

A nickname is separate from a username. People will see it instead of the username in most cases.

Ex. `rename user seisatsu Overlord Seisatsu`"""

def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2, wizard=True):
        return False

    # Lookup target user.
    targetuser = COMMON.check_user(NAME, console, args[0].lower())
    if not targetuser:
        return False

    # Make sure the name is not an integer, as this would be confusing.
    # We actually want an exception to be raised here.
    if len(args) == 2:
        try:
            int(''.join(args[1:]))
            console.msg("{0}: The nickname cannot be an integer.".format(NAME))
            return False
        except ValueError:
            # Not an integer.
            pass

    # Get new nickname.
    nickname = ' '.join(args[1:])
    if nickname == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Make sure a user with this nickname does not already exist.
    # Make an exception if that user is us. (changing case)
    if console.database.user_by_nick(nickname) and nickname.lower() != targetuser["nick"].lower():
        console.msg("{0}: That nickname is already in use.".format(NAME))
        return False

    # Rename the target.
    targetuser["nick"] = nickname
    console.database.upsert_user(targetuser)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
