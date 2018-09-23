import blackbox
import console
import database

router = {}
dbman = database.DatabaseManager("testdb")

HOST = "irc.datnode.net"
PORT = 6667
NICKNAME = "Dennis"
USERNAME = "Dennis"
REALNAME = "Dennis"
CHANNEL = "#dennis"

irc = blackbox.IRC()
parser = blackbox.Parser()
irc.connect(HOST, PORT)
irc.nickname(NICKNAME)
irc.username(USERNAME, REALNAME)

joined = False
while True:
    data = irc.recv()
    event = parser.parse(data)
    user = event.user()
    nick = event.origin()[1:]
    if joined is False and event.command == "376":
        irc.join(CHANNEL)
    if user and event.command == "PRIVMSG":
        if user not in router:
            router[user] = console.Console(dbman, lambda msg: irc.say(nick, msg))
        if user in router:
            print(' '.join(event.params[1:]))
            router[user].command(' '.join(event.params[1:]))
