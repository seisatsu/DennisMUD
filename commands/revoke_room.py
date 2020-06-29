#####################
# Dennis MUD        #
# revoke_room.py    #
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

NAME = "revoke room"
CATEGORIES = ["rooms"]
ALIASES = ["unshare room"]
USAGE = "revoke room <username>"
DESCRIPTION = """Remove user <username> from the owners of the current room.

You must be an owner of the room in order to revoke ownership from another user.
You can grant ownership with the `grant room` command, provided you are an owner.

Ex. `grant room seisatsu`"""


def COMMAND(console, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    roomid = console.user["room"]
    r = console.database.room_by_id(roomid)

    # Make sure we are the room's owner.
    if console.user["name"] not in r["owners"]:
        console.msg(NAME + ": you do not own this room")
        return False

    # Make sure the named user exists.
    u = console.database.user_by_name(args[0].lower())
    if not u:
        console.msg(NAME + ": no such user")
        return False

    # Check if the named user is an owner.
    if not args[0].lower() in r["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": user already not an owner of this room")
        return False

    r["owners"].remove(args[0].lower())
    console.database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
