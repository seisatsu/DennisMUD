##########################
# Dennis MUD             #
# undecorate_entrance.py #
# Copyright 2020         #
# Michael D. Reiley      #
##########################

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

NAME = "undecorate entrance"
CATEGORIES = ["exits"]
USAGE = "undecorate entrance <exit_id>"
DESCRIPTION = """Remove the custom action displayed when a player enters the next room through <exit_id>.

You must own the exit or its room in order to undecorate its entrance.
Wizards can undecorate any entrance.

Ex. `undecorate entrance 3`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    exitid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if exitid is None:
        return False

    # Lookup the current room, and perform exit checks.
    thisroom = COMMON.check_exit(NAME, console, exitid, owner=True)
    if not thisroom:
        return False

    # Check if the entrance is already undecorated.
    if not thisroom["exits"][exitid]["action"]["entrance"]:
        console.msg("{0}: This entrance already has no custom action.".format(NAME))
        return False

    # Undecorate the entrance.
    thisroom["exits"][exitid]["action"]["entrance"] = ""
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True

