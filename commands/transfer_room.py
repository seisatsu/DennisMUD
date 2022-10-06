#####################
# Dennis MUD        #
# transfer_room.py  #
# Copyright 2020    #
# Sei Satzparad     #
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

NAME = "transfer room"
CATEGORIES = ["rooms", "ownership"]
USAGE = "transfer room <username>"
DESCRIPTION = """Give primary ownership of the current room to the user <username>.

You must be the primary owner of the room in order to transfer it.
You will be downgraded to secondary ownership of the room.
Wizards can transfer any room.

Ex. `transfer room seisatsu`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console, primary=True, owner=True)
    if not thisroom:
        return False

    # Make sure the named user exists.
    targetuser = COMMON.check_user(NAME, console, args[0].lower())
    if not targetuser:
        return False

    # Make the user the primary owner, removing them first if they are a secondary owner.
    # This will automatically make the current user a secondary owner by pushing them to the second list position.
    if args[0].lower() in thisroom["owners"]:
        thisroom["owners"].remove(args[0].lower())
    thisroom["owners"].insert(0, args[0].lower())
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
