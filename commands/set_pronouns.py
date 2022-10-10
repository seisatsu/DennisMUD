#######################
# Dennis MUD          #
# set_pronouns.py     #
# Copyright 2020-2022 #
# Sei Satzparad       #
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

NAME = "set pronouns"
CATEGORIES = ["actions", "settings", "users"]
USAGE = "set pronouns [neutral|female|male]|[custom <they> <them> <their> <theirs> <themselves>]"
DESCRIPTION = """Check or set your pronouns for formatting action and posturing text.

The default setting is neutral. Without an argument, just check the current setting.
You can either choose from the predefined neutral, female, and male pronoun settings, or define your own.

To define your own pronouns, use `set pronouns custom <args>`, where <args> is the list of which words will replace the markers %they%, %them%, %their%, %theirs%, and %themselves%, in that order.

Ex. `set pronouns female` to set female pronouns.
Ex. `set pronouns custom xe xem xir xirs xirself` to set custom xe/xem/xir pronouns."""


def COMMAND(console, args):
    max_length = console.database.defaults["users"]["pronouns"]["maxlength"]

    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=0, argmax=6):
        return False

    # Just check our current pronouns.
    if len(args) == 0:
        console.msg("{0}: Your pronouns are currently set to {1}.".format(NAME, console.user["pronouns"]))
        return True
    
    # Make sure we have a correct number of arguments otherwise.
    if (len(args) > 1 and args[0] not in ["c", "custom"]) or (len(args) != 6 and args[0] in ["c", "custom"]):
        console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
        return False
    
    # Make sure we chose an available option, and update the user's pronouns setting.
    if args[0].lower() in ["f", "female"]:
        console.user["pronouns"] = "female"
    elif args[0].lower() in ["m", "male"]:
        console.user["pronouns"] = "male"
    elif args[0].lower() in ["n", "neutral"]:
        console.user["pronouns"] = "neutral"
    elif args[0].lower() in ["c", "custom"]:
        for pronoun in args[1:]:
            if len(pronoun) > max_length:
                console.msg("{0}: Custom pronouns cannot be longer than {1} characters.".format(NAME, max_length))
                return False
        console.user["pronouns"] = args[1:]
    else:
        console.msg("{0}: Must choose one of: \"female\", \"male\", \"neutral\", \"common\".".format(NAME))
        return False
    console.database.upsert_user(console.user)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
