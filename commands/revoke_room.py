#######################
# Dennis MUD          #
# revoke_room.py      #
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

NAME = "revoke room"
CATEGORIES = ["rooms", "ownership"]
ALIASES = ["unshare room"]
USAGE = "revoke room <username>"
DESCRIPTION = """Remove the user <username> from the owners list of the current room.

You must be an owner of the room in order to revoke ownership from another user.
You cannot revoke ownership from the primary owner, even if they are you.
You can grant ownership with the `grant room` command, provided you are an owner.
Wizards can revoke ownership of any room.

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

    # Check if the named user is already not an owner.
    if args[0].lower() in thisroom["owners"]:
        console.msg("{0}: That user is already not an owner of this room.".format(NAME))
        return False

    # Check if the named user is the primary owner.
    if thisroom["owners"][0] == args[1].lower():
        console.msg("{0}: You cannot revoke ownership from the primary owner.".format(NAME))
        return False

    # Revoke the room from the user.
    thisroom["owners"].remove(args[0].lower())
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
