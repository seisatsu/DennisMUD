#######################
# Dennis MUD          #
# describe_item.py    #
# Copyright 2018-2020 #
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

NAME = "describe item"
CATEGORIES = ["items"]
USAGE = "describe item <item_id> <description>"
DESCRIPTION = """Set the description of the item <item_id> which you are holding.

A double backslash inserts a newline. Two sets of double backslashes make a paragraph break.
You may have any number of newlines, but you cannot stack more than two together.
You must own the item and it must be in your inventory in order to describe it.
Wizards can describe any item from anywhere.

You may also want to change the action text that players will see when using the item.
See the `actionate item` command.

Ex. `describe item 4 A small music box made of ivory.`
Ex2. `describe item 4 A small music box made of ivory.\\\\The bottom edge of the lid is lined with silver trim.`
Ex3. `describe item 4 A small music box made of ivory.\\\\\\\\The bottom edge of the lid is lined with silver trim.`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2):
        return False

    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False

    # Process any newlines and then describe the item.
    if "\\\\" * 3 in ' '.join(args[1:]):
        console.msg("{0}: You may only stack two newlines.".format(NAME))
        return False
    thisitem["desc"] = ' '.join(args[1:]).replace("\\\\", "\n")
    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True
