#######################
# Dennis MUD          #
# seal_outbound.py    #
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

NAME = "seal outbound"
CATEGORIES = ["exits", "rooms"]
USAGE = "seal outbound"
DESCRIPTION = """Prevent any exits from being added, removed, or redirected in the current room.

You must own the current room in order to seal it.
Only an owner of the room will be able to add, remove, or redirect the exits here.
It will still be possible for an exit owner to rename, describe, or decorate an exit, but not to redirect it.
You can reverse this with the `unseal outbound` command.
Wizards can seal any room, and ignore room seals."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console, owner=True)
    if not thisroom:
        return False

    # Check if the room is already outbound sealed.
    if thisroom["sealed"]["outbound"]:
        console.msg("{0}: This room is already outbound sealed.".format(NAME))
        return False

    # Seal the room's outbound.
    thisroom["sealed"]["outbound"] = True
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
