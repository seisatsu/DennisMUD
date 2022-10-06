#######################
# Dennis MUD          #
# grant_exit.py       #
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

NAME = "grant exit"
CATEGORIES = ["exits", "ownership"]
ALIASES = ["share exit"]
USAGE = "grant exit <exit_id> <username>"
DESCRIPTION = """Add user <username> to the owners of the exit <exit_id> in the current room.

You must type the full username.
You must own the exit in order to grant it to another user.
You will also retain ownership of the exit.
You can revoke ownership with the `revoke exit` command, provided you are an owner.
Wizards can grant any exit to anyone.

Ex. `grant exit 3 seisatsu`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=2):
        return False

    # Perform argument type checks and casts.
    exitid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if exitid is None:
        return False

    # Lookup the current room, and perform exit checks.
    thisroom = COMMON.check_exit(NAME, console, exitid, owner=True)
    if not thisroom:
        return False

    # Make sure the named user exists.
    targetuser = COMMON.check_user(NAME, console, args[1].lower())
    if not targetuser:
        return False

    # Check if the named user is already an owner.
    if args[1].lower() in thisroom["exits"][exitid]["owners"]:
        console.msg("{0}: That user is already an owner of this exit.".format(NAME))
        return False

    # Grant the exit to the user.
    thisroom["exits"][exitid]["owners"].append(args[1].lower())
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
