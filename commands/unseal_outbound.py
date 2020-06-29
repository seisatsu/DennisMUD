######################
# Dennis MUD         #
# unseal_outbound.py #
# Copyright 2020     #
# Michael D. Reiley  #
######################

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

NAME = "unseal outbound"
CATEGORIES = ["exits", "rooms"]
USAGE = "unseal outbound"
DESCRIPTION = """Allow exits to be added, removed, or modified in the current room.

You must own the current room in order to unseal it.
Undoes outbound sealing the room via the `seal outbound` command."""


def COMMAND(console, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    roomid = console.user["room"]
    r = console.database.room_by_id(roomid)

    # Make sure we are the room's owner.
    if console.user["name"] not in r["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this room")
        return False

    if not r["sealed"]["outbound"]:
        console.msg(NAME + ": this room is already outbound unsealed")
        return False
    r["sealed"]["outbound"] = False
    console.database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
