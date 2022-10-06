#######################
# Dennis MUD          #
# telnet.py           #
# Copyright 2018-2021 #
# Sei Satzparad       #
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

# Parts of codebase borrowed from https://github.com/TKeesh/WebSocketChat

import traceback

from lib.logger import Logger

from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver

# Read the motd file.
try:
    with open("motd.telnet.txt") as f:
        motd = f.read()
except:
    motd = None


class ServerProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.peer = None
        self._log = Logger("telnet")

    def connectionMade(self):
        p = self.transport.getPeer()
        self.peer = p.host + ':' + str(p.port)
        self.factory.register(self)
        self._log.info("Client connected: {peer}", peer=self.peer)
        if motd:
            self.factory.communicate(self.peer, motd.encode('utf-8'))

    def connectionLost(self, reason):
        self.factory.unregister(self)
        self._log.info("Client disconnected: {peer}", peer=self.peer)

    def lineReceived(self, line):
        # Don't log passwords.
        passcheck = line.split(b' ')
        if passcheck[0] == b'login' and len(passcheck) > 2:
            passcheck = b' '.join(passcheck[:2] + [b'********'])
            self._log.info("Client {peer} sending message: {line}", peer=self.peer, line=passcheck)
        elif passcheck[0] == b'register' and len(passcheck) > 2:
            passcheck = b' '.join(passcheck[:2] + [b'********'])
            self._log.info("Client {peer} sending message: {line}", peer=self.peer, line=passcheck)
        elif passcheck[0] == b'password' and len(passcheck) > 1:
            passcheck = b' '.join(passcheck[:1] + [b'********'])
            self._log.info("Client {peer} sending message: {line}", peer=self.peer, line=passcheck)
        else:
            self._log.info("Client {peer} sending message: {line}", peer=self.peer, line=line)

        # Try to decode the line.
        try:
            line = line.decode('utf-8')
        except:
            self._log.info("Discarded garbage line from {peer}", peer=self.peer)
            return

        # Did we receive the quit pseudo-command?
        if line == "quit":
            self.transport.loseConnection()
            return

        # Run the command while handling errors.
        try:
            self.factory.router.shell.command(self.factory.router[self.peer]["console"], line)
        except:
            self.factory.communicate(self.peer, traceback.format_exc().encode('utf-8'))
            self._log.error(traceback.format_exc())


class ServerFactory(protocol.Factory):

    def __init__(self, router, *args, **kwargs):
        self.router = router
        self.router.telnet_factory = self
        super(ServerFactory, self).__init__(*args)
        self.clients = []

    def buildProtocol(self, addr):
        return ServerProtocol(self)

    def register(self, client):
        self.clients.append({'client-peer': client.peer, 'client': client})
        self.router.register(client.peer, "telnet")

    def unregister(self, client):
        self.router.unregister(client.peer)
        for c in self.clients:
            if c['client-peer'] == client.peer:
                self.clients.remove(c)

    def communicate(self, peer, payload):
        client = None
        for c in self.clients:
            if c['client-peer'] == peer:
                client = c['client']
        if client:
            # Telnet wants a CRLF instead of just an LF. Some clients require this to display properly.
            client.sendLine(payload.decode('utf-8').replace('\n', '\r\n').encode('utf-8'))
