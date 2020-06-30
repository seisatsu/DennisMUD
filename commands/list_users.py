#####################
# Dennis MUD        #
# list_users.py     #
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

NAME = "list users"
CATEGORIES = ["users"]
USAGE = "list users"
DESCRIPTION = """List all online users in the world.

If you are a wizard, you will see a list of all registered users, including offline users."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Sort all users in the database by username.
    users = sorted(console.database.users.all(), key=lambda k: k["name"])

    # Iterate through the users, checking whether each one is online or offline,
    # and keeping track of how many were online vs offline.
    online_count = 0
    offline_count = 0
    if len(users):
        for thisuser in users:
            # Everyone can see which users are online. List them out and keep count.
            if console.database.online(thisuser["name"]):
                console.msg("{0} ({1})".format(thisuser["nick"], thisuser["name"]))
                online_count += 1

        # If we are a wizard, iterate through again and list out the offline users this time, and keep count.
        if console.user["wizard"]:
            for thisuser in users:
                if not console.database.online(thisuser["name"]):
                    console.msg("{0} ({1}) [offline]".format(thisuser["nick"], thisuser["name"]))
                    offline_count += 1

            # Format the count of online and offline users for wizards.
            console.msg("total users online: {0}; offline: {1}".format(online_count, offline_count))

        else:
            # Format the count of just online users for regular players.
            console.msg("total users online: {0}".format(online_count))

    # This shouldn't ever happen.
    else:
        console.log.error("no users returned from list users command")
        console.msg("{0}: error: no users?!".format(NAME))

    # Finished.
    return True
