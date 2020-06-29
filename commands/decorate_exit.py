#####################
# Dennis MUD        #
# decorate_exit.py  #
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

NAME = "decorate exit"
CATEGORIES = ["exits"]
USAGE = "decorate exit <id> <action>"
DESCRIPTION = """Set a custom <action> to display when a player uses the exit <id> in the current room.

By default, the action text is shown following the player's nickname and one space.
To place the player's name elsewhere in the text, use the %player% marker.
You must own the exit or its room in order to decorate it.
You can remove the custom action from an exit with the `undecorate exit` command.

Ex. `decorate exit 3 falls through the floor.`
Ex2. `decorate exit 3 The floor opens up under %player%'s feet.`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2):
        return False

    # Perform argument type checks and casts.
    exitid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if exitid is None:
        return False

    # Lookup the current room, and perform exit checks.
    thisroom = COMMON.check_exit(NAME, console, exitid)
    if not thisroom:
        return False

    # Check if we have permission to decorate the exit.
    if console.user["name"] not in thisroom["exits"][exitid]["owners"] \
            and console.user["name"] not in thisroom["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this exit or this room")
        return False

    # Decorate the exit.
    thisroom["exits"][exitid]["action"]["go"] = ' '.join(args[1:])
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg(NAME + ": done")
    return True
