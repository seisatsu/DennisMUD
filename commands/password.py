#####################
# Dennis MUD        #
# password.py       #
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

import hashlib

NAME = "password"
CATEGORIES = ["users"]
USAGE = "password [username] <password>"
DESCRIPTION = """Change your password.

You must be logged in. The username argument is optional.
Only wizards can change the passwords of other users.
 
Ex. `password n3wp4ss`
Ex2. `password seisatsu n3wp4ss`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1, argmax=2):
        return False

    # We only gave one argument or named ourselves, so change our own password.
    if len(args) == 1 or (len(args) == 2 and args[0].lower() == console.user["name"]):
        console.user["passhash"] = hashlib.sha256(args[len(args)-1].encode()).hexdigest()
        recovery = str(int(hashlib.sha256(console.user["passhash"].encode()).hexdigest(), 16))[-6:]
        console.database.upsert_user(console.user)

    # We are a wizard and named another user, so change their password.
    elif console.user["wizard"]:
        # Make sure the named user exists.
        targetuser = COMMON.check_user(NAME, console, args[0].lower())
        if not targetuser:
            return False

        # Change their password.
        targetuser["passhash"] = hashlib.sha256(args[1].encode()).hexdigest()
        recovery = str(int(hashlib.sha256(targetuser["passhash"].encode()).hexdigest(), 16))[-6:]
        console.database.upsert_user(targetuser)

    # We named another user, but we aren't a wizard.
    else:
        console.msg("{0}: Only a wizard can change another user's password".format(NAME))
        return False

    # Finished.
    console.msg("{0}: The password has been changed.".format(NAME))
    console.msg("The NEW account recovery code is \"{0}\".".format(recovery))
    return True
