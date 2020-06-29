#######################
# Dennis MUD          #
# disable_autolook.py #
# Copyright 2020      #
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

NAME = "disable autolook"
CATEGORIES = ["exploration", "settings"]
USAGE = "disable autolook"
DESCRIPTION = """Disable autolook. You will no longer automatically look upon entering a room.

You can enable autolook with the `enable autolook` command."""


def COMMAND(console, args):
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    # Check if autolook is already disabled.
    if not console.user["autolook"]["enabled"]:
        console.msg(NAME + ": autolook is already disabled")
        return False

    console.user["autolook"]["enabled"] = False
    console.database.upsert_user(console.user)

    console.msg(NAME + ": done")
    return True
