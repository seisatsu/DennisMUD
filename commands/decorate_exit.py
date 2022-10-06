#######################
# Dennis MUD          #
# decorate_exit.py    #
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

NAME = "decorate exit"
CATEGORIES = ["actions", "exits"]
USAGE = "decorate exit <exit_id> <action>"
DESCRIPTION = """Set a custom <action> to broadcast when a player uses the exit <exit_id> in the current room.

Everyone in the current room will see the action text when it is broadcast.
By default, the action text is shown following the player's nickname and one space.
If the action starts with 's then the space is removed to allow possessive grammar.
To place the player's name elsewhere in the text, use the "%player%" marker.
To just message the player and not include their name, start the text with "%noaction%".
The tags "%they%", "%them%", "%their%", "%theirs%", and "%themselves%" will substitute pronouns.
The pronouns substituted will depend on the player's pronoun setting. See `set pronouns`.
The "%s%" tag will be removed for neutral pronouns, and otherwise replaced with the letter "s".
You must own the exit or its room in order to decorate it.
You can remove the custom action from an exit with the `undecorate exit` command.
Wizards can decorate any exit.

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
    thisroom = COMMON.check_exit(NAME, console, exitid, owner=True)
    if not thisroom:
        return False

    # Decorate the exit.
    thisroom["exits"][exitid]["action"]["go"] = ' '.join(args[1:])
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
