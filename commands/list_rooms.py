#####################
# Dennis MUD        #
# list_rooms.py     #
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

NAME = "list rooms"
CATEGORIES = ["rooms"]
USAGE = "list rooms"
DESCRIPTION = """List all rooms in the world that you own.

If you are a wizard, you will see a list of all rooms that exist."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Sort all rooms in the database by ID.
    allrooms = sorted(console.database.rooms.all(), key=lambda k: k["id"])

    # Iterate through the rooms, checking whether we own each one (or are a wizard),
    # and keeping track of whether we found anything at all.
    found_something = False
    for thisroom in allrooms:
        # We either own this room, or we are a wizard. List it out.
        if console.user["name"] in thisroom["owners"] or console.user["wizard"]:
            console.msg("{0} ({1})".format(thisroom["name"], thisroom["id"]))
            found_something = True

    # We found nothing. At least the first room must exist, so that means we just don't own any rooms.
    if not found_something:
        console.msg("{0}: you do not own any rooms".format(NAME))

    # Finished.
    return True
