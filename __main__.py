import console
import database
import pdb

dbman = database.DatabaseManager("testdb")
dennis = console.Console(dbman)
dennis.command("login sei temp")
dennis.user.wizard = True
dennis.command("list rooms")
dennis.help("greater break item")

