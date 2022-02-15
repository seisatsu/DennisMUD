#######################
# Dennis MUD          #
# remake_exit.py      #
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

NAME = "remake exit"
CATEGORIES = ["exits"]
USAGE = "remake exit <exit_id>"
DESCRIPTION = """Resets the exit <exit_id> in this room.

Destination, name and owner list are untouched.
You must own the exit or its room.
Wizards can remake any exit.

Ex. `remake exit 3`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1, argmax=1):
        return False

    # Perform argument type checks and casts.
    exitid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if exitid is None:
        return False

    # Lookup the current room, and perform exit checks.
    thisroom = COMMON.check_exit(NAME, console, exitid, owner=True)
    if not thisroom:
        return False

    # remake the exit.
    thisroom["exits"][exitid]["desc"] = ""
    thisroom["exits"][exitid]["key"] = None
    thisroom["exits"][exitid]["key_hidden"] = True
    thisroom["exits"][exitid]["locked"] = False
    thisroom["exits"][exitid]["hidden"] = False
    thisroom["exits"][exitid]["chance"] = 1
    thisroom["exits"][exitid]["action"]["go"] = ""
    thisroom["exits"][exitid]["action"]["locked"] = ""
    thisroom["exits"][exitid]["action"]["entrance"] = ""
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True

