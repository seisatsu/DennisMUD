#####################
# Dennis MUD        #
# lost_exit.py      #
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

NAME = "lock exit"
CATEGORIES = ["exits"]
USAGE = "lock exit <id>"
DESCRIPTION = """Prevents anyone except the exit owner or a key holder from using the exit <id> in this room.

Any player who is not holding the key to the exit and does not own the exit will be unable to pass.
You must own the exit or its room in order to lock it.
You can unlock a locked exit with the `unlock exit` command.

Ex. `lock exit 3`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    exitid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if exitid is None:
        return False

    # Lookup the current room, and perform exit checks.
    thisroom = COMMON.check_exit(NAME, console, exitid)
    if not thisroom:
        return False

    # Make sure we own the exit or the room, or we are a wizard.
    if console.user["name"] not in thisroom["exits"][exitid]["owners"] \
            and console.user["name"] not in thisroom["owners"] and not console.user["wizard"]:
        console.msg("{0}: you do not own this exit or this room".format(NAME))
        return False

    # Check if the exit is already locked.
    if thisroom["exits"][exitid]["locked"]:
        console.msg("{0}: this exit is already locked".format(NAME))
        return False

    # Lock the exit.
    thisroom["exits"][exitid]["locked"] = True
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: done".format(NAME))
    return True
