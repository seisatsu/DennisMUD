#####################
# Dennis MUD        #
# lay.py            #
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

NAME = "lay"
CATEGORIES = ["actions", "settings", "users"]
ALIASES = ["lay down", "lay on", "lay down on"]
USAGE = "lay [item_name]"
DESCRIPTION = """Lay down, on the ground or on the item [item_name].

This will perform an action and modify your description to let other players know you are laying down.
You can stand back up by using `stand` or by using `lay` a second time. You may also `sit`.
If an item is given, you will lay down on that item. Otherwise you will just lay down.
You cannot lay down on an item that is in your inventory; it must be in the room.
The modification to your description is affected by your pronouns; see `set pronouns`.

Ex. `lay`
Ex2. `lay down`
Ex3. `lay on bed`
Ex4. `lay down on bed`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args):
        return False

    # Check if we are already laying down. If so, stand up, unless arguments are given.
    if console["posture"] and not args:
        if console["posture"] == "laying down":
            return COMMON.posture(NAME, console)

    # If no arguments were given, and we aren't laying down already, lay on the floor.
    if not args:
        return COMMON.posture(NAME, console, "laying down", "lays down")

    # Arguments were given. Make sure the player didn't try to lay on an item by its ID instead of its name.
    try:
        int(' '.join(args))
        console.msg("{0}: Requires a name, not an ID.".format(NAME))
        return False
    except:
        pass

    # Try to lay on the named item.
    return COMMON.posture(NAME, console, "laying down", "lays down", ' '.join(args))
