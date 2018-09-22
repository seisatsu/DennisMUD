import console
import database
import pdb

dbman = database.DatabaseManager("testdb")
dennis = console.Console(dbman)
dennis.command("register sei temp")
pdb.set_trace()

