#####################
# Dennis MUD        #
# locate_user.py    #
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

NAME = "locate user"
CATEGORIES = ["users"]
ALIASES = ["find user"]
USAGE = "locate user <name>"
DESCRIPTION = """Find out what room the user with username <name> is in.

This only works with usernames, not with nicknames.
See the `realname` command to derive a user's username from their nickname.
If a user is offline, only wizards can see their location.

Ex. `locate user seisatsu`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Make sure the named user exists.
    targetuser = COMMON.check_user(NAME, console, args[0].lower())
    if not targetuser:
        return False

    # Lookup the user's room and perform room checks.
    userroom = COMMON.check_room(NAME, console, targetuser["room"], reason=False)
    if not userroom:
        console.log.error("room does not exist for user: {user} -> {room}",
                          user=args[0].lower(), room=targetuser["room"])
        console.msg("{0}: error: room does not exist for user")
        return False

    # If the target user is online, show their location.
    if console.database.online(args[0].lower()):
        console.msg("{0}: {1} is in room {2} ({3})".format(NAME, targetuser["name"], userroom["name"], userroom["id"]))
        return True

    # If the target user is offline but we are a wizard, show their location anyway.
    elif console.user["wizard"]:
        console.msg("{0}: {1} (offline) is in room {2} ({3})".format(NAME, targetuser["name"], userroom["name"],
                                                                     userroom["id"]))
        return True

    # User is not online and we are not a wizard. Just say they are offline.
    else:
        console.msg("{0}: {1} is offline".format(NAME, targetuser["name"]))
        return True
