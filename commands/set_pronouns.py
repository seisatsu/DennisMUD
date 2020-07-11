#####################
# Dennis MUD        #
# set_pronouns.py   #
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

NAME = "set pronouns"
CATEGORIES = ["settings", "users"]
USAGE = "set pronouns [female|male|neutral]"
DESCRIPTION = """Check or set your pronouns for formatting posturing text.

The default setting is neutral. Without an argument, just check the current setting.

Ex. `set pronouns female` to set female pronouns."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=0, argmax=1):
        return False

    # Just check our current pronouns.
    if len(args) == 0:
        console.msg("{0}: Your pronouns are currently set to {1}.".format(NAME, console.user["pronouns"]))
        return True

    # Make sure we chose an available option.
    if args[0].lower() in ["f", "female"]:
        console.user["pronouns"] = "female"
    elif args[0].lower() in ["m", "male"]:
        console.user["pronouns"] = "male"
    elif args[0].lower() in ["n", "neutral"]:
        console.user["pronouns"] = "neutral"
    else:
        console.msg("{0}: Must choose one of: \"female\", \"male\", \"neutral\".".format(NAME))
        return False
    console.database.upsert_user(console.user)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
