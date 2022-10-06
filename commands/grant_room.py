#######################
# Dennis MUD          #
# grant_room.py       #
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

NAME = "grant room"
CATEGORIES = ["rooms", "ownership"]
ALIASES = ["share room"]
USAGE = "grant room <username>"
DESCRIPTION = """Add user <username> to the owners of the current room.

You must type the full username.
You must own the room in order to grant it to another user.
You will also retain ownership of the room.
You can revoke ownership with the `revoke room` command, provided you are an owner.
Wizards can grant any room to anyone.

Ex. `grant room seisatsu`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console, owner=True)
    if not thisroom:
        return False

    # Make sure the named user exists.
    targetuser = COMMON.check_user(NAME, console, args[0].lower())
    if not targetuser:
        return False

    # Check if the named user is already an owner.
    if args[0].lower() in thisroom["owners"]:
        console.msg("{0}: That user is already an owner of this room.".format(NAME))
        return False

    # Grant the room to the user.
    thisroom["owners"].append(args[0].lower())
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
