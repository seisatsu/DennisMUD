#######################
# Dennis MUD          #
# perform.py          #
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
import random

NAME = "perform"
CATEGORIES = ["actions","users"]
ALIASES = ["miracle", "cast", "ritual"]
SCOST=0
USAGE = "perform <ritual> <optional ...>"
DESCRIPTION = """Perform the ritual called <ritual>. 

Current rituals: telepathy, identify, reveal.

Ex. `perform telepathy seisatsu Hello there!`
Ex1. `perform reveal`"""


def COMMAND(console, args):
    # Perform initial checks.
    if not COMMON.check(NAME, console, args, argmin=1):
        return False

    elif args[0]=="force":
        console.msg("Not implemented yet.")
        return False

    elif args[0]=="reveal":
        SCOST=5
        if not COMMON.check(NAME, console, args, argmax=1, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"]):
            return False
        
        destroom = COMMON.check_room(NAME,console)
        dexits = destroom["exits"]
        for dex in range(len(dexits)):
            # Check for randomized chance
            if dexits[dex]["chance"] and dexits[dex]["hidden"]==True:
                if random.randint(1,dexits[dex]["chance"])==1: 
                    dexits[dex]["hidden"]=False

        # Random items check.
        ditems = destroom["items"]
        for dit in ditems:
            dit = console.database.item_by_id(dit)
            # Check for randomized chance
            if dit["chance"] and dit["hidden"]==True:
                if random.randint(1,dit["chance"])==1: 
                    dit["hidden"]=False
                # A small chance to reveal truly hidden stuff.
                if random.randint(1,4)==1:
                    dit["truehide"]=False

        msg = "{0} tries to reveal hidden things with a ritual.".format(console.user["nick"])
        console.shell.broadcast_room(console, msg)
        return True

    elif args[0]=="identify":
        # Spirit cost of identify.
        SCOST=5
        found_something = False
        partials = []
        target=' '.join(args[1:])
        if not COMMON.check(NAME, console, args, argmin=2, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"]):
            return False
        
        # Lookup the current room and perform room checks.
        thisroom = COMMON.check_room(NAME, console)
        if not thisroom:
            return False

        # It wasn't us, so maybe it's an item in the room.
        for itemid in thisroom["items"]:
            item = console.database.item_by_id(itemid)
            # A reference was found to a nonexistent item. Report this and continue searching.
            if not item:
                console.log.error("Item referenced in room does not exist: {room} :: {item}", room=console.user["room"],
                                  item=itemid)
                console.msg("{0}: ERROR: Item referenced in this room does not exist: {1}".format(NAME, itemid))
                continue
            attributes = []

            # Record partial matches.
            if target in item["name"].lower() or target.replace("the ", "", 1) in item["name"].lower():
                partials.append(item["name"].lower())

            # It was an item in the room. Show the item's name, ID, owners, description, and attributes.
            if target in [item["name"].lower(), "the " + item["name"].lower()]:
                # Only enumerate item attributes if we are the item owner or a wizard.
                if item["duplified"]:
                    attributes.append("This thing can be anywhere, somehow at the same time.")
                if item["cursed"]["enabled"]:
                    attributes.append("A dark presence haunts it.")
                if item["glued"]:
                    attributes.append("This object can't be carried with you.")
                if item["truehide"]:
                    attributes.append("Maybe it's invisible, but something truly hides it from sight.")
                if item["hidden"]:
                    attributes.append("Somehow it blends into it's environment.")
                if item["lang"]:
                    attributes.append("You sense that this thing can teach you and alter your language.")
                if item["container"]["enabled"]:
                    attributes.append("Something else could easily fit into the insides of this object.")
                if item["telekey"]:
                    attributes.append("Using this thing would take you somewhere else.")

                # Send the info for this item.
                if len(attributes)>0:
                    console.msg("You sense the {0}. {1}".format(item["name"], ' '.join(attributes)))    
                else:
                    console.msg("You sense the {0}.".format(item["name"]))
                console.msg("It seems to be connected to {0}.".format(', '.join(item["owners"])))

                # Description exists, so show it.
                #if item["desc"]:
                #    console.msg(item["desc"])

                # List content if it's a container
                if len(item["container"]["inventory"])>0 and item["container"]["enabled"]:
                    console.msg("{0} seems to contain some items.".format(item["name"].capitalize()))
                else:
                    console.msg("{0} seems to be empty.".format(item["name"].capitalize()))
                found_something = True
                return True

        # Maybe it's an item in our inventory.
        for itemid in console.user["inventory"]:
            item = console.database.item_by_id(itemid)
            # A reference was found to a nonexistent item. Report this and continue searching.
            if not item:
                console.log.error("Item referenced in user inventory does not exist: {user} :: {item}",
                                  user=console.user["name"], item=itemid)
                console.msg("{0}: ERROR: Item referenced in your inventory does not exist: {1}".format(NAME, itemid))
                continue
            attributes = []

            # Record partial matches.
            if target in item["name"].lower() or target.replace("the ", "", 1) in item["name"].lower():
                partials.append(item["name"].lower())

            # It was an item in our inventory. Show the item's name, ID, owners, description, and attributes,
            # but only if we didn't already see it in the current room. Also check if the user prepended "the ".
            if target in [item["name"].lower(), "the " + item["name"].lower()]:
                # Only enumerate item attributes if we are the item owner or a wizard.
                if item["duplified"]:
                    attributes.append("This thing can be anywhere, somehow at the same time.")
                if item["cursed"]["enabled"]:
                    attributes.append("A dark presence haunts it.")
                if item["glued"]:
                    attributes.append("This object can't be carried with you.")
                if item["truehide"]:
                    attributes.append("Maybe it's invisible, but something truly hides it from sight.")
                if item["hidden"]:
                    attributes.append("Somehow it blends into it's environment.")
                if item["lang"]:
                    attributes.append("You sense that this thing can teach you and alter your language.")
                if item["container"]["enabled"]:
                    attributes.append("Something else could easily fit into the insides of this object.")
                if item["telekey"]:
                    attributes.append("Using this thing would take you somewhere else.")

                # Send the info for this item.
                if len(attributes)>0:
                    console.msg("You sense the {0}. {1}".format(item["name"], ' '.join(attributes)))    
                else:
                    console.msg("You sense the {0}.".format(item["name"]))
                console.msg("It seems to be connected to {0}.".format(', '.join(item["owners"])))

                # Description exists, so show it.
                #if item["desc"]:
                #    console.msg(item["desc"])

                # List content if it's a container
                if len(item["container"]["inventory"])>0 and item["container"]["enabled"]:
                    console.msg("{0} seems to contain some items.".format(item["name"].capitalize()))
                else:
                    console.msg("{0} seems to be empty.".format(item["name"].capitalize()))

                found_something = True
                return True
        # We didn't find anything by that name. See if we found partial matches.
        if not found_something:
            # Eliminate duplicate matches.
            if partials:
                partials = list(dict.fromkeys(partials))

            # We got exactly one partial match. Assume that one.
            if len(partials) == 1:
                console.msg("Assuming {0}.".format(partials[0]))
                console.user["spirit"]+=SCOST
                partials[0]="identify "+partials[0]
                return COMMAND(console, partials[0].split(' '))

            # We got up to 5 partial matches. List them.
            elif partials and len(partials) <= 5:
                console.msg("{0}: Did you mean one of: {1}".format(NAME, ', '.join(partials)))
                return False

            # We got too many matches.
            elif len(partials) > 5:
                console.msg("{0}: Too many possible matches.".format(NAME))
                return False

            # Really nothing.
            else:
                console.msg("{0}: No such thing: {1}".format(NAME, ' '.join(args[1:])))
            return False
        
    elif args[0]=="telepathy":
        # Spirit cost of telepathy.
        SCOST=5
        if not COMMON.check(NAME, console, args, argmin=3, spiritcost=SCOST, spiritenabled=CONFIG["spiritenabled"]):
            return False
        
        # Make sure the named user exists and is online.
        targetuser = COMMON.check_user(NAME, console, args[1].lower(), online=True)
        if not targetuser:
            return False

        # Finished. Message the user, and echo the message to ourselves, if it wasn't a self-message.
        console.shell.msg_user(args[1].lower(), mcolor(CBYELLO,"You hear a whisper in your mind: '{0}'".format(' '.join(args[2:])),targetuser["colors"]["enabled"]))
        if targetuser["name"] != console.user["name"]:
            console.msg(mcolor(CBYELLO,"You plant a message in the mind of {0}, that says: '{1}'".format(targetuser["name"], ' '.join(args[2:])),console.user["colors"]["enabled"]))
        msg = "{0} focuses for a moment to perform a ritual.".format(console.user["nick"])
        console.shell.broadcast_room(console, msg)
        return True
    else:
        console.msg("You never heard of such a ritual.")
        return False

