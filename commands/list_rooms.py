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
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    rooms = sorted(console.database.rooms.all(), key=lambda k: k["id"])
    found_something = False
    if len(rooms):
        for r in rooms:
            if console.user["name"] in r["owners"] or console.user["wizard"]:
                # We either own this room, or we are a wizard.
                console.msg("{0} ({1})".format(r["name"], r["id"]))
                found_something = True
    if not found_something:
        console.msg(NAME + ": you do not own any rooms")

    return True
