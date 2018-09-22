import console
import database
import pdb

dbman = database.DatabaseManager("testdb")
dennis = console.Console(dbman)
while True:
    cmd = input("> ").lower()
    dennis.command(cmd)

