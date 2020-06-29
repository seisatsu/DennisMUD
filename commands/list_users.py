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
    if len(args) != 0:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False

    users = sorted(console.database.users.all(), key=lambda k: k["name"])
    online_count = 0
    offline_count = 0
    if len(users):
        for u in users:
            if console.database.online(u["name"]):
                console.msg("{0} ({1})".format(u["nick"], u["name"]))
                online_count += 1
        if console.user["wizard"]:
            for u in users:
                if not console.database.online(u["name"]):
                    console.msg("{0} ({1}) [offline]".format(u["nick"], u["name"]))
                    offline_count += 1
            console.msg("total users online: {0}; offline: {1}".format(online_count, offline_count))
        else:
            console.msg("total users online: {0}".format(online_count))
    else:
        console.msg(NAME + ": no users?!")

    return True
