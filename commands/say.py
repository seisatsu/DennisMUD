#######################
# Dennis MUD          #
# say.py              #
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

from lib.color import *

NAME = "say"
CATEGORIES = ["messaging"]
SPECIAL_ALIASES = ['\"']
USAGE = "say <message>"
DESCRIPTION = """Send a message to everyone in the current room.

These messages cannot be ignored.

Ex. `say Hello everyone!`
Ex2. `"Hello everyone!`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Broadcast our message to the current room.
    args[0]=args[0].capitalize()
    if args[-1][-1]=="?": console.shell.broadcast_room(console, CBCYAN+"{0} asks, '{1}'".format(console.user["nick"], ' '.join(args)+CRES))
    elif args[-1].count("!")>1: console.shell.broadcast_room(console, CBCYAN+"{0} yells, '{1}'".format(console.user["nick"], ' '.join(args)+CRES))
    elif args[-1][-1]=="!": console.shell.broadcast_room(console, CBCYAN+"{0} exclaims, '{1}'".format(console.user["nick"], ' '.join(args)+CRES))
    else:
        #Talk nice. 
        if args[-1][-1]!=".": args[-1]=args[-1]+"."
        console.shell.broadcast_room(console, CBCYAN+"{0} says, '{1}'".format(console.user["nick"], ' '.join(args)+CRES))

    # Finished.
    return True
