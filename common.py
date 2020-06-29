#####################
# Dennis MUD        #
# common.py         #
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

# This module contains code for various tasks that need to be performed by commands fairly often.
# It is imported globally as COMMON.

from tinydb.table import Document


def check(NAME, console, args, argc=None, argmin=None, argmax=None, online=True, wizard=False,
          usage=True, reason=True):
    """Perform simple checks.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param args: The args passed to the command.
    :param argc: The arg count to enforce.
    :param argmin: The arg count minimum to enforce.
    :param argmax: The arg count maximum to enforce.
    :param online: Whether to check if the user is online. Defaults to True.
    :param wizard: Whether to check if the user is a wizard.
    :param usage: Whether to print usage for the command if the check fails. Defaults to True.
    :param reason: Whether to print a common failure explanation if the check fails. Defaults to True.

    :return: True if succeeded, False if failed.
    """
    caller = console.shell._commands[NAME]

    # Check argument count.
    if argc is None:
        pass
    elif len(args) != argc:
        if usage:
            console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
        return False

    # Check argument minimum.
    if argmin is None:
        pass
    elif len(args) < argmin:
        if usage:
            console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
        return False

    # Check argument maximum.
    if argmax is None:
        pass
    elif len(args) > argmax:
        if usage:
            console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
        return False

    # Check if the calling user is logged in.
    if online:
        if not console.user:
            if reason:
                console.msg(NAME + ": must be logged in first")
            return False

    # Check if the calling user is a wizard.
    if wizard:
        if not console.user["wizard"]:
            if reason:
                console.msg(NAME + ": you do not have permission to use this command")
            return False

    return True


def check_argtypes(NAME, console, args, checks, retargs=None, cast=True, usage=True):
    """Perform checks on the types of args passed to a command.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param args: The args passed to the command.
    :param checks: A list or tuple of pairs in the form ((arg_index, expected_type)...).
    :param retargs: If set, an int, list, or tuple of arg index(es) to return from the original args on success.
    :param cast: Whether to cast the argument if returning it.
    :param usage: Whether to print usage for the command if the check fails.

    :return: True if succeeded, False if failed.
    """
    castargs = args

    if type(checks) not in (list, tuple):
        console.log.error("checks type mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return False

    for chk in checks:
        if type(chk) not in (list, tuple):
            console.log.error("checks type mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return False
        if chk[0] >= len(args):
            console.log.error("checks index mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return False
        try:
            # Try to cast the arg at the given index as the given type.
            castargs[chk[0]] = chk[1](args[chk[0]])
        except ValueError:
            if usage:
                console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
            return False

    if retargs is None:
        pass
    elif type(retargs) is int:
        if retargs >= len(args):
            console.log.error("retargs index mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return False
        if cast:
            return castargs[retargs]
        return args[retargs]
    elif type(retargs) in (list, tuple):
        retval = []
        for ret in retargs:
            if ret >= len(args):
                console.log.error("retargs index mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
                console.msg("{0}: internal command error".format(NAME))
                return False
            if cast:
                retval.append(castargs[ret])
            else:
                retval.append(args[ret])
        return retval
    else:
        console.log.error("retargs type mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return False

    return True


def check_wizard(NAME, console, reason=True):
    """Just check if the user is a wizard.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param reason: Whether to print a common failure explanation if the check fails. Defaults to True.

    :return: True if succeeded, False if failed.
    """
    if not console.user["wizard"]:
        if reason:
            console.msg(NAME + ": you do not have permission to use this command")
        return False
    return True


def check_exit(NAME, console, exitid, room=None, reason=True):
    """Check if an exit exists in a room.
    
    For convenience, also checks the room and returns the room document if the room was found.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param room: The room id or room document of the room to check if set, otherwise the user's current room.
    :param reason: Whether to print a common failure explanation if the check fails. Defaults to True.
    
    :return: Room document if succeeded, None if failed.
    """
    try:
        exitid = int(exitid)
    except ValueError:
        console.log.error("exitid type mismatch in COMMON.check_exit from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    if room is None:
        thisroom = console.database.room_by_id(console.user["room"])
    elif type(room) is int:
        thisroom = console.database.room_by_id(room)
    elif type(room) is Document:
        thisroom = room
    else:
        console.log.error("room type mismatch in COMMON.check_exit from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    if not thisroom:
        if room is None:
            console.log.error("current room does not exist for user: {user} ({room})", user=console.user["name"],
                              room=console.user["room"])
            console.msg("error: current room does not exist")
        console.log.error("nonexistent room in COMMON.check_exit from command: {name}", name=NAME)
        if reason:
            console.msg(NAME + ": no such exit")
        return None

    if exitid > len(thisroom["exits"]) - 1 or exitid < 0:
        if reason:
            console.msg(NAME + ": no such exit")
        return None
    return thisroom


def check_item(NAME, console, itemid, reason=True):
    """Check if an item exists. If so, return it.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param itemid: The item id of the item to check.
    :param reason: Whether to print a common failure explanation if the check fails. Defaults to True.

    :return: Item document if succeeded, None if failed.
    """
    try:
        itemid = int(itemid)
    except ValueError:
        console.log.error("itemid type mismatch in COMMON.check_item from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    item = console.database.item_by_id(itemid)
    if not item:
        if reason:
            console.msg(NAME + ": no such item")
        return None
    return item


def check_room(NAME, console, roomid=None, reason=True):
    """Check if a room exists. If so, return it.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param roomid: The room id of the room to check if set, otherwise the user's current room.
    :param reason: Whether to print a common failure explanation if the check fails. Defaults to True.

    :return: Room document if succeeded, None if failed.
    """
    if roomid is None:
        roomid = console.user["room"]
    else:
        try:
            roomid = int(roomid)
        except ValueError:
            console.log.error("roomid type mismatch in COMMON.check_room from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return None
    
    room = console.database.room_by_id(roomid)
    if not room:
        if roomid is None:
            console.log.error("current room does not exist for user: {user} ({room})", user=console.user["name"],
                              room=console.user["room"])
            console.msg("error: current room does not exist")
            return None
        elif reason:
            console.msg(NAME + ": no such room")
        return None
    return room

