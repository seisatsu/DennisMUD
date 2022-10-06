#######################
# Dennis MUD          #
# unhide_key.py       #
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

NAME = "unhide key"
CATEGORIES = ["exits"]
USAGE = "unhide key <exit_id>"
DESCRIPTION = """Allow looking at the locked exit <exit_id> to reveal the name of its key.

If the key for an exit is not hidden, looking at the exit will tell the player the name of the item which unlocks it.
You must own the exit or its room to unhide the key.
Wizards can unhide the key for any exit.

Ex. `unhide key 3`"""


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

    # Make sure there is a key paired to this exit.
    if not thisroom["exits"][exitid]["key"]:
        console.msg("{0}: There is no key paired to this exit.".format(NAME))
        return False

    # Check if the key is already not hidden.
    if not thisroom["exits"][exitid]["key_hidden"]:
        console.msg("{0}: The key for this exit is already not hidden.".format(NAME))
        return False

    # Unhide the key.
    thisroom["exits"][exitid]["key_hidden"] = False
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
