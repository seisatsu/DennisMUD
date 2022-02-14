#######################
# Dennis MUD          #
# language_user.py      #
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

NAME = "language user"
CATEGORIES = ["wizards"]
USAGE = "language user <name> <language>"
DESCRIPTION = """Set a target player's language to <language>.

A language is mostly just a flavor of a character. People not speaking the same language will see encoded text. This command is mostly for wizards for debug purposes.

Ex. `language seisatsu unknown`"""

def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2, argmax=2, wizard=True):
        return False

    # Lookup target user.
    targetuser = COMMON.check_user(NAME, console, args[0].lower())
    if not targetuser or args[1].isalpha()==False:
        return False

    # Make sure the name is not an integer, as this would be confusing.
    # We actually want an exception to be raised here.
    try:
        int(args[1])
        console.msg("{0}: The language cannot be an integer.".format(NAME))
        return False
    except ValueError:
        # Not an integer.
        pass

    # Get new nickname.
    langname = args[1]
    if langname == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # language the target.
    targetuser["lang"] = langname
    console.database.upsert_user(targetuser)

    # Finished.
    console.msg("{0}: Done. Language of {1} is {2} now.".format(NAME,args[0],langname))
    return True
