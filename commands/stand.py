#####################
# Dennis MUD        #
# stand.py          #
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

NAME = "stand"
CATEGORIES = ["actions", "settings", "users"]
ALIASES = ["stand up"]
USAGE = "stand"
DESCRIPTION = """Stand up if currently in another posture.

This will perform an action and modify your description if you are currently taking a posture.
Commands that make you take a posture include `sit` and `lay`.

Ex. `stand`
Ex2. `stand up`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Check if we are already standing up. If so, don't do anything. Otherwise, stand up.
    if not console["posture"]:
        console.msg("{0}: You are already standing up.".format(NAME))
        return False
    else:
        return COMMON.posture(NAME, console)
