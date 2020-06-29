#####################
# Dennis MUD        #
# lost_exit.py      #
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

NAME = "lock exit"
CATEGORIES = ["exits"]
USAGE = "lock exit <id>"
DESCRIPTION = """Prevents anyone except the exit owner or a key holder from using the exit <id> in this room.

Any player who is not holding the key to the exit and does not own the exit will be unable to pass.
You must own the exit or its room in order to lock it.
You can unlock a locked exit with the `unlock exit` command.

Ex. `lock exit 3`"""


def COMMAND(console, args):
    if len(args) != 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    try:
        exitid = int(args[0])
    except ValueError:
        console.msg("Usage: " + USAGE)
        return False

    roomid = console.user["room"]
    r = console.database.room_by_id(roomid)

    # Make sure the exit exists.
    if exitid > len(r["exits"]) - 1 or exitid < 0:
        console.msg(NAME + ": no such exit")
        return False

    # Make sure we own the exit or the room.
    if console.user["name"] not in r["exits"][exitid]["owners"] \
            and console.user["name"] not in r["owners"] and not console.user["wizard"]:
        console.msg(NAME + ": you do not own this exit or this room")
        return False

    if r["exits"][exitid]["locked"]:
        console.msg(NAME + ": this exit is already locked")
        return False
    r["exits"][exitid]["locked"] = True
    console.database.upsert_room(r)
    console.msg(NAME + ": done")
    return True
