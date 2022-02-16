#######################
# Dennis MUD          #
# alter_item.py    #
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

NAME = "alter item"
CATEGORIES = ["items"]
USAGE = "alter item <item_id> <item_type>"
DESCRIPTION = """Set the type of the item with <item_id>.

Currently supported item types are:
- simple
- book
- container
- cursed

If the item type is not default then it's a special item like a book 
for learning languages. They don't necessarily need to look and used like a book.
Wizards can alter any item from anywhere. The item type simple basically resets the other types.

Ex. `alter item 4 book`
Ex2. `alter item 4 simple"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=2):
        return False
    types=["simple", "book", "container", "cursed"]
    # Perform argument type checks and casts.
    itemid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if itemid is None:
        return False

    # Lookup the target item and perform item checks.
    thisitem = COMMON.check_item(NAME, console, itemid, owner=True, holding=True)
    if not thisitem:
        return False

    # alter the item.
    if args[1] not in types:
        console.msg("Not a valid item type. Currently items can be one of these: {0}".format(', '.join(types)))
        return False
    if args[1]=="simple":
        thisitem["lang"] = None
        if(len(thisitem["container"]["inventory"]))>0:
            console.msg("Can't make it a non-container, please empty the item first.")
            return False
        else: thisitem["container"]["enabled"] = False
    elif args[1]=="book":
        thisitem["lang"] = console.user["lang"]
    elif args[1]=="cursed":
        if thisitem["cursed"]["enabled"]:
           thisitem["cursed"]["enabled"] = False
        else:    
            thisitem["cursed"]["enabled"] = True
    elif args[1]=="container":
        if "into" in thisitem["name"] or "from" in thisitem["name"]:
            console.msg("Containers can't have the word INTO or FROM in their name. Please rename the item before making it a container.")
            return False
        thisitem["container"]["enabled"] = True
        thisitem["container"]["inventory"] = []
    console.database.upsert_item(thisitem)

    # Finished.
    console.msg("{0}: Done. {1} is now a {2} item.".format(NAME,args[0].capitalize(),args[1]))
    return True
