NAME = "demote"
USAGE = "demote [username]"
DESCRIPTION = "(WIZARDS ONLY) Remove wizard status from yourself or the named user."


def COMMAND(console, database, args):
    if len(args) > 1:
        console.msg("Usage: " + USAGE)
        return False

    # Make sure we are logged in, and a wizard.
    if not console.user:
        console.msg(NAME + ": must be logged in first")
        return False
    if not console.user["wizard"]:
        console.msg(NAME + ": you do not have permission to use this command")
        return False

    if len(args) == 0:
        # Demote ourselves.
        console.user["wizard"] = False
        database.upsert_user(console.user)
    else:
        # Demote the named user.
        targetuser = database.user_by_name(args[0])
        if not targetuser:
            # No such user.
            console.msg(NAME + ": no such user")
            return False
        targetuser["wizard"] = False
        database.upsert_user(targetuser)

    console.msg(NAME + ": done")
    return True
