#######################
# Dennis MUD          #
# randomize_exit.py    #
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

NAME = "randomize exit"
CATEGORIES = ["exits"]
USAGE = "randomize exit <exit_id> <chance>"
DESCRIPTION = """Set the chance of the exit <exit_id> appearing in this room.

You must own the exit or its room in order to randomize it.
Wizards can randomize any exit and also see them all the time.
Chance is optional, without giving a chance it just shows you the currently set one.

Ex. `randomize exit 3` shows you the chance for id 3.
Ex2. `randomize exit 3 1 (100% chance)`
Ex3. `randomize exit 3 10 (10% chance)`
Ex4. `randomize exit 3 100 (1% chance)`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1, argmax=2):
        return False

    # Perform argument type checks and casts.
    exitid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if exitid is None:
        return False
    if len(args)==2:
        exitchance = COMMON.check_argtypes(NAME, console, args, checks=[[1, int]], retargs=1)
        if exitchance is None:
            return False

    # Lookup the current room, and perform exit checks.
    thisroom = COMMON.check_exit(NAME, console, exitid, owner=True)
    if not thisroom:
        return False

    # Process any newlines and then randomize the exit.
    if len(args)<2:
        console.msg("That exit has a 1 out of {0} chance to appear.".format(thisroom["exits"][exitid]["chance"]))
    else:    
        if exitchance<1:
            console.msg("{0}: Chance must be greater than 0.".format(NAME))
            return False
        thisroom["exits"][exitid]["chance"] = exitchance
        thisroom["exits"][exitid]["hidden"] = False
        console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True

