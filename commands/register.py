#######################
# Dennis MUD          #
# register.py         #
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

import hashlib
import string

NAME = "register"
CATEGORIES = ["users"]
USAGE = "register <username> <password>"
DESCRIPTION = """Register a new user with <username> and <password>.

Afterwards, you can join the game with the `login` command.
This will also provide you with a 6-digit recovery key, which you should write down.
The recovery key will allow you to change your password with the `recover` command if you lose it.

Ex. `register seisatsu mypassword`"""

# Allowed characters for new username registrations.
ALLOWED_CHARACTERS = string.ascii_letters + string.digits + '_'


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=2, online=False):
        return False

    # Make sure we are not already logged in.
    if console.user:
        console.msg("{0}: You must logout first to register a new user.".format(NAME))
        return False

    # Check allowed characters.
    for char in args[0]:
        if char not in ALLOWED_CHARACTERS:
            console.msg("{0}: Usernames may contain alphanumerics and underscores only.".format(NAME))
            return False
    if args[0].lower() == "the":
        console.msg("{0}: Very funny.".format(NAME))
        return False

    # Make sure the username isn't already taken.
    if console.database.user_by_name(args[0].lower()):
        console.msg("{0}: That username is already registered.".format(NAME))
        return False

    # Generate password hash and six digit recovery code.
    passhash = hashlib.sha256(args[1].encode()).hexdigest()
    recovery = str(int(hashlib.sha256(passhash.encode()).hexdigest(), 16))[-6:]

    # Create and save a new user.
    newuser = {
        "name": args[0].lower(),
        "nick": args[0],
        "desc": "",
        "passhash": hashlib.sha256(args[1].encode()).hexdigest(),
        "room": 0,
        "inventory": [],
        "pronouns": "neutral",
        "pronouno": "neutral",
        "pronounp": "neutral",
        "wizard": False,
        "autolook": {
            "enabled": console.database.defaults["users"]["autolook"]["enabled"]
        },
        "builder": {
            "enabled": console.database.defaults["users"]["builder"]["disabled"]
        },
        "cecho": {
            "enabled": console.database.defaults["users"]["cecho"]["enabled"]
        },
        "chat": {
            "enabled": console.database.defaults["users"]["chat"]["enabled"],
            "ignored": []
        }
    }
    console.database.upsert_user(newuser)

    # Confirm the registration, and give recovery code.
    console.msg("Registered user \"{0}\".".format(newuser["name"]))
    console.msg("Your account recovery code is \"{0}\". Please write it down.".format(recovery))
    console.msg("If you lose your password, you can use `recover <username> <code> <newpass>` to change it.")
    console.msg("Otherwise, you will have to contact the administrator of this server.")
    return True
