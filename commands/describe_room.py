#######################
# Dennis MUD          #
# describe_room.py    #
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

NAME = "describe room"
CATEGORIES = ["rooms"]
USAGE = "describe room <description>"
DESCRIPTION = """Set the description of the room you are in.

A double backslash inserts a newline. Two sets of double backslashes make a paragraph break.
You may have any number of newlines, but you cannot stack more than two together.
You must own the room in order to describe it.
Wizards can describe any room.

Ex. `describe room 5 You are standing in a long, dark hallway.`
Ex2. `describe room 5 You are standing in a long, dark hallway.\\\\You cannot see the end.`
Ex3. `describe room 5 You are standing in a long, dark hallway.\\\\\\\\You cannot see the end.`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    # Lookup the current room and perform room checks.
    thisroom = COMMON.check_room(NAME, console, owner=True)
    if not thisroom:
        return False

    # Process any newlines and then describe the room.
    if "\\\\" * 3 in ' '.join(args):
        console.msg("{0}: You may only stack two newlines.".format(NAME))
        return False
    thisroom["desc"] = ' '.join(args).replace("\\\\", "\n")
    console.database.upsert_room(thisroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
