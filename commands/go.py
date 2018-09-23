from datatype import Room, User, Item

USAGE = "go <exit>"
DESCRIPTION = "Take the exit called <exit> to wherever it may lead."


def COMMAND(console, database, args):
        if len(args) == 0:
            return False

        # Look for the exit in the current room.
        thisroom = database.filter(Room, {"id": console.user.room})
        if not len(thisroom):
            return False  # The current room does not exist?!
        thisroom = thisroom[0]

        exits = thisroom["exits"]
        if len(exits):
            for e in exits:
                if e["name"].lower() == ' '.join(args).lower():
                    # Check if the destination room exists.
                    destroom = database.filter(Room, {"id": e["dest"]})
                    if not len(destroom):
                        return False  # The destination room does not exist.
                    destroom = destroom[0]

                    # Move us to the new room.
                    if console.user.name in thisroom:
                        thisroom.users.remove(console.user.name)
                    destroom.users.append(console.user.name)
                    console.user.room = destroom.id
                    database.update(thisroom)
                    database.update(destroom)
                    database.update(console.user)
                    return True

        return False
