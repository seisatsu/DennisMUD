#######################
# Dennis MUD          #
# rename_exit.py      #
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

NAME = "rename exit"
CATEGORIES = ["exits"]
USAGE = "rename exit <id> <name>"
DESCRIPTION = """Set the name of the exit <id> in this room to <name>.

You must own the exit or its room.

Ex. `rename exit 3 Iron Door`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2):
        return False

    # Perform argument type checks and casts.
    exitid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if exitid is None:
        return False

    # Lookup the current room, and perform exit checks.
    thisroom = COMMON.check_exit(NAME, console, exitid, owner=True)
    if not thisroom:
        return False

    # Make sure the exit name is not an integer, as this would be confusing.
    # We actually want an exception to be raised here.
    if len(args) == 2:
        try:
            int(args[1])
            console.msg("{0}: The exit name cannot be an integer.".format(NAME))
            return False
        except ValueError:
            # Not an integer.
            pass

    # Get new exit name.
    exitname = ' '.join(args[1:])
    if exitname == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Make sure an exit by this name does not already exist in the current room.
    # Make an exception if that is the exit we are renaming. (changing case)
    exits = thisroom["exits"]
    for ex in exits:
        if ex["name"].lower() == exitname.lower() and ex["name"].lower() != thisroom["exits"][exitid]["name"].lower():
            console.msg("{0}: An exit by that name already exists in this room.".format(NAME))
            return False

    # Rename the exit.
    thisroom["exits"][exitid]["name"] = exitname
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True

