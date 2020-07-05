#####################
# Dennis MUD        #
# break_room.py     #
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

NAME = "break room"
CATEGORIES = ["rooms"]
ALIASES = ["delete room", "destroy room", "remove room"]
USAGE = "break room <room>"
DESCRIPTION = """Break the room with ID <room> if you are its owner.

You must be an owner of the room, and no one can be in the room, including yourself.

Ex. `break room 5` to break the room with ID 5."""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argc=1):
        return False

    # Perform argument type checks and casts.
    roomid = COMMON.check_argtypes(NAME, console, args, checks=[[0, int]], retargs=0)
    if roomid is None:
        return False

    # Lookup the target room and perform room checks.
    targetroom = COMMON.check_room(NAME, console, roomid, owner=True)
    if not targetroom:
        return False

    # Make sure the room is empty.
    if targetroom["users"]:
        console.msg("{0}: You cannot break an occupied room.".format(NAME))
        return False

    # If the room contains items, return them to their primary owners.
    for itemid in targetroom["items"]:
        # Lookup the target item and perform item checks.
        thisitem = COMMON.check_item(NAME, console, itemid)
        if not thisitem:
            console.log.error("Item referenced in room does not exist: {room} :: {item}", room=roomid, item=itemid)
            console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
            continue

        # Make sure the primary owner exists.
        targetuser = COMMON.check_user(NAME, console, thisitem["owners"][0], live=True)
        if not targetuser:
            console.log.error("Primary owner of item does not exist: {item} :: {user}", item=itemid,
                              user=thisitem["owners"][0])
            console.msg("{0}: ERROR: Primary owner of item in this room does not exist: {1} :: {2}".format(
                NAME, itemid, thisitem["owners"][0]))
            continue

        # Don't return the item to the primary owner if they already have it. (Could be duplified.)
        if itemid not in targetuser["inventory"]:
            targetuser["inventory"].append(itemid)
            console.shell.msg_user(thisitem["owners"][0], "{0} appeared in your inventory.".format(
                COMMON.format_item(NAME, thisitem["name"], upper=True)))
        console.database.upsert_user(targetuser)

    # Remove this room from the entrances record of every room it has an exit to.
    for ex in targetroom["exits"]:
        destroom = console.database.room_by_id(ex["dest"])
        if targetroom["id"] in destroom["entrances"]:
            destroom["entrances"].remove(targetroom["id"])
            console.database.upsert_room(destroom)

    # Unpair all telekey items that are paired to this room.
    for item in console.database.items.all():
        if item["telekey"] == roomid:
            item["telekey"] = None
            console.database.upsert_item(item)

    # Delete the room.
    console.database.delete_room(targetroom)

    # Finished.
    console.msg("{0}: Done.".format(NAME))
    return True


