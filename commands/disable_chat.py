#####################
# Dennis MUD        #
# disable_chat.py   #
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

NAME = "disable chat"
CATEGORIES = ["messaging", "settings"]
USAGE = "disable chat"
DESCRIPTION = """Disable the general chat. You will not be able to receive or send chat messages.

You can enable the general chat with the `enable chat` command.

Chat messages are separate from private messages and same-room communication."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=0):
        return False

    # Check if chat is already disabled.
    if not console.user["chat"]["enabled"]:
        console.msg("{0}: chat is already disabled".format(NAME))
        return False

    # Disable chat.
    console.user["chat"]["enabled"] = False
    console.database.upsert_user(console.user)

    # Finished.
    console.msg("{0}: done".format(NAME))
    return True
