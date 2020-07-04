#####################
# Dennis MUD        #
# sit.py            #
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

NAME = "sit"
CATEGORIES = ["settings", "users"]
ALIASES = ["sit down", "sit on", "sit down on"]
USAGE = "sit [item]"
DESCRIPTION = """Sit down, on the ground or on the named item.

This will perform an action and modify your description to let other players know you are sitting down.
You can stand back up by using `stand` or by using `sit` a second time. You may also `lay`.
If an item is given, you will sit down on that item. Otherwise you will just sit down.
You cannot sit down on an item that is in your inventory; it must be in the room.

Ex. `sit`
Ex2. `sit down`
Ex3. `sit on carpet`
Ex4. `sit down on carpet`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args):
        return False

    # Check if we are already sitting down. If so, stand up, unless arguments are given.
    if console["posture"] and not args:
        if console["posture"] == "sitting down":
            return COMMON.posture(NAME, console)

    # If no arguments were given, and we aren't sitting down already, sit on the floor.
    if not args:
        return COMMON.posture(NAME, console, "sitting down", "sits down")

    # Arguments were given. Make sure the player didn't try to sit on an item by its ID instead of its name.
    try:
        int(' '.join(args))
        console.msg("{0}: Requires a name, not an ID.".format(NAME))
        return False
    except:
        pass

    # Try to sit on the named item.
    return COMMON.posture(NAME, console, "sitting down", "sits down", ' '.join(args))
