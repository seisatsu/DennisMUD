import console
import database


class Router:
    def __init__(self):
        pass

    def message(self, nickname, msg):
        pass

    def broadcast_all(self, msg):
        pass

    def broadcast_room(self, room, msg):
        pass


dbman = database.DatabaseManager("localhost", 27017, "dennis2")
dennis = console.Console(dbman, None, Router())
while True:
    cmd = input("> ")
    print(dennis.command(cmd))
