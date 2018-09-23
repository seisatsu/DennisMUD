import blackbox
import console
import database
import json

router = {}

with open("config.json") as f:
    config = json.load(f)

dbman = database.DatabaseManager(config["database"])
irc = blackbox.IRC()
parser = blackbox.Parser()
irc.connect(config["host"], config["port"])
irc.nickname(config["nickname"])
irc.username(config["username"], config["realname"])

joined = False
while True:
    data = irc.recv()
    event = parser.parse(data)
    user = event.user()
    nick = event.origin()[1:]
    if joined is False and event.command == "376":
        for channel in config["channels"]:
            irc.join(channel)
    if user and event.command == "PRIVMSG":
        if user not in router:
            router[user] = console.Console(dbman, lambda msg: irc.say(nick, msg))
        if user in router:
            print(' '.join(event.params[1:]))
            router[user].command(' '.join(event.params[1:]))
