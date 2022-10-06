#######################
# Dennis MUD          #
# promote.py          #
# Copyright 2018-2020 #
# Sei Satzparad       #
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

NAME = "promote"
CATEGORIES = ["wizard"]
USAGE = "promote <username>"
DESCRIPTION = """(WIZARDS ONLY) Elevate the named user to wizard status.

Ex. `promote seisatsu`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1, wizard=True):
        return False

    # Lookup the target user and perform user checks.
    targetuser = COMMON.check_user(NAME, console, args[0].lower(), wizard=False, live=True, reason=True, already=True)
    if not targetuser:
        return False

    # Promote the user.
    targetuser["wizard"] = True
    console.database.upsert_user(targetuser)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
