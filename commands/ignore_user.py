#######################
# Dennis MUD          #
# ignore_user.py      #
# Copyright 2018-2020 #
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

NAME = "ignore user"
CATEGORIES = ["messaging", "settings", "users"]
USAGE = "ignore user <username>"
DESCRIPTION = """Ignore general chat messages and private messages from the user <username>.

You must type the full username.
If you ignore a user, you will not see their messages in chat, or any private messages they attempt to send you.
An ignored user will not be informed that you have ignored them.
If the ignored user is in the same room as you, you will still hear what they `say`.
You can unignore an ignored user with the `unignore user` command.
Wizards cannot be ignored.

Ex. `ignore user seisatsu` won't do anything because seisatsu is a wizard.
Ex2. `ignore user loser` will prevent you from receiving messages from loser."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Lookup target user.
    targetuser = COMMON.check_user(NAME, console, args[0].lower())
    if not targetuser:
        return False

    # Check if the target user is already ignored.
    if targetuser["name"] in console.user["chat"]["ignored"]:
        console.msg("{0}: You are already ignoring that user.".format(NAME))
        return False

    # Check if the target user is a wizard.
    if targetuser["wizard"]:
        console.msg("{0}: Wizards cannot be ignored.".format(NAME))
        return False

    # Ignore the user.
    console.user["chat"]["ignored"].append(targetuser["name"])
    console.database.upsert_user(console.user)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
