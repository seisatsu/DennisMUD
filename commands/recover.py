#####################
# Dennis MUD        #
# recover.py        #
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

import hashlib

NAME = "recover"
CATEGORIES = ["users"]
USAGE = "recover [<username> <code> <newpass>]"
DESCRIPTION = """Use your recovery code to change your password, or see the current code.

If you get locked out of your account, you can change your password without logging in.
This requires the recovery code you were given when you registered an account.
If you have lost the code as well, you will need to contact this server's administrator.
If there are no arguments, and you are logged in, just show the current recovery code.
Changing the password will also change the recovery code.
Wizards can retrieve any user's recovery code by providing their username as the only argument.

Ex. `recover seisatsu 847630 myn3wp4ssw0rd`"""


def COMMAND(console, args):
    # Check for illegal command usages.
    if len(args) == 2 or (len(args) != 3 and not console.user):
        console.msg("Usage: recover [<username> <code> <newpass>]")
        return False

    # If there is only one argument, we are trying to get the recovery code for a particular user.
    # Only wizards can get another user's code.
    elif len(args) == 1 and not console.user["wizard"] and args[0].lower() != console.user["name"]:
        console.msg("{0}: Only a wizard can retrieve another user's recovery code.".format(NAME))
        return False

    # If there is one argument and it is our own name, just pretend the command was called with zero arguments.
    elif len(args) == 1 and args[0].lower() == console.user["name"]:
        args = []
        pass

    # We are a wizard, and requesting another user's recovery code.
    elif len(args) == 1:
        targetuser = COMMON.check_user(NAME, console, args[0].lower())
        if not targetuser:
            return False
        recovery = str(int(hashlib.sha256(targetuser["passhash"].encode()).hexdigest(), 16))[-6:]
        console.msg("{0}: Recovery code for user: {1} :: {2}".format(NAME, args[0].lower(), recovery))
        return True

    # No arguments, so just return the current recovery code for a logged in user.
    if len(args) == 0:
        if not console.user:
            console.msg("{0}: Must be logged in to retrieve current recovery code.".format(NAME))
            console.msg("Usage: recover [<username> <code> <newpass>]")
            return False
        else:
            recovery = str(int(hashlib.sha256(console.user["passhash"].encode()).hexdigest(), 16))[-6:]
            console.msg("{0}: Your current recovery code is \"{1}\". Please write it down.".format(NAME, recovery))
            return True

    # This is a recovery attempt. Make sure we aren't getting brute forced.
    if console._login_delay:
        console.msg("{0}: Wait a second before trying again.".format(NAME))
        return False

    # Make sure the named user exists and the recovery code is correct.
    targetuser = COMMON.check_user(NAME, console, args[0].lower(), reason=False)
    if not targetuser or args[1] != str(int(hashlib.sha256(targetuser["passhash"].encode()).hexdigest(), 16))[-6:]:
        console.msg("{0}: Incorrect recovery code for username: {1}".format(NAME, args[0].lower()))
        console._login_delay = True
        console.router._reactor.callLater(1, console._reset_login_delay)
        return False

    # Change the password.
    targetuser["passhash"] = hashlib.sha256(args[2].encode()).hexdigest()
    recovery = str(int(hashlib.sha256(targetuser["passhash"].encode()).hexdigest(), 16))[-6:]
    console.database.upsert_user(targetuser)

    # Finished.
    console.msg("{0}: Your password has been changed and you may now log in.".format(NAME))
    console.msg("Your NEW account recovery code is \"{0}\". Please write it down.".format(recovery))
    return True
