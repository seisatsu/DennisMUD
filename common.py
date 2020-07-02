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
                console.msg("{0}: must be logged in first".format(NAME))
            return False

    # Check if the calling user is a wizard.
    if wizard:
        if not console.user["wizard"]:
            if reason:
                console.msg("{0}: you do not have permission to use this command".format(NAME))
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

    :return: True or args if succeeded, None if failed.
    """
    castargs = args.copy()

    if type(checks) not in (list, tuple):
        console.log.error("checks type mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    for chk in checks:
        if type(chk) not in (list, tuple):
            console.log.error("checks type mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return None
        if chk[0] >= len(args):
            console.log.error("checks index mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return None
        try:
            # Try to cast the arg at the given index as the given type.
            castargs[chk[0]] = chk[1](args[chk[0]])
        except ValueError:
            if usage:
                console.msg("Usage: {0}".format(console.shell._commands[NAME].USAGE))
            return None

    if retargs is None:
        pass
    elif type(retargs) is int:
        if retargs >= len(args):
            console.log.error("retargs index mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
            console.msg("{0}: internal command error".format(NAME))
            return None
        if cast:
            return castargs[retargs]
        return args[retargs]
    elif type(retargs) in (list, tuple):
        retval = []
        for ret in retargs:
            if ret >= len(args):
                console.log.error("retargs index mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
                console.msg("{0}: internal command error".format(NAME))
                return None
            if cast:
                retval.append(castargs[ret])
            else:
                retval.append(args[ret])
        return retval
    else:
        console.log.error("retargs type mismatch in COMMON.check_argtypes from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    return True


def check_exit(NAME, console, exitid, room=None, reason=True):
    """Check if an exit exists in a room.
    
    For convenience, also checks the room and returns the room document if the room was found.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param exitid: The exit id of the exit to check.
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
            console.msg("{0}: error: current room does not exist".format(NAME))
        console.log.error("nonexistent room in COMMON.check_exit from command: {name}", name=NAME)
        if reason:
            console.msg("{0}: no such exit".format(NAME))
        return None

    elif exitid > len(thisroom["exits"]) - 1 or exitid < 0:
        if reason:
            console.msg("{0}: no such exit".format(NAME))
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
            console.msg("{0}: no such item".format(NAME))
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
            console.msg("{0}: error: current room does not exist".format(NAME))
            return None
        elif reason:
            console.msg("{0}: no such room".format(NAME))
        return None
    return room


def check_user(NAME, console, username, online=False, wizard=None, live=False, reason=True, already=False):
    """Check if a user exists. If so, return it.

    :param NAME: The NAME field from the command module.
    :param console: The calling user's console.
    :param username: The username of the user to check.
    :param online: Whether to check if the user is online.
    :param wizard: If True, check if the user is a wizard. If False, check if the user is not a wizard.
    :param live: Whether to try to grab the live copy of the user document instead of pulling from the database.
    :param reason: Whether to print a common failure explanation if the check fails. Defaults to True.
    :param already: Whether to include the word "already" in the wizard failure explanation.

    :return: User document if succeeded, None if failed.
    """
    if type(username) is not str:
        console.log.error("username type mismatch in COMMON.check_user from command: {name}", name=NAME)
        console.msg("{0}: internal command error".format(NAME))
        return None

    username = username.lower()

    if live:
        user = console.shell.user_by_name(username)
    else:
        user = console.database.user_by_name(username)

    if not user:
        if reason:
            console.msg("{0}: no such user".format(NAME))
        return None

    elif online and not console.database.online(username):
        if reason:
            console.msg("{0}: user is not online".format(NAME))
        return None

    elif wizard is not None:
        if wizard and not user["wizard"]:
            if reason:
                if already:
                    console.msg("{0}: user is already not a wizard".format(NAME))
                else:
                    console.msg("{0}: user is not a wizard".format(NAME))
            return None
        elif user["wizard"] and not wizard:
            if reason:
                if already:
                    console.msg("{0}: user is already a wizard".format(NAME))
                else:
                    console.msg("{0}: user is a wizard".format(NAME))
            return None

    return user
