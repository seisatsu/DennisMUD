########################
# Dennis MUD           #
# telnet-backend.py    #
# Copyright 2018       #
# Michael D. Reiley    #
########################

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

from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver


class ServerProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.peer = None

    def connectionMade(self):
        p = self.transport.getPeer()
        self.peer = p.host + ':' + str(p.port)
        print("Client connecting: {0}".format(self.peer))
        self.factory.register(self)
        print("Client connected: {0}".format(self.peer))

    def connectionLost(self, reason):
        self.factory.unregister(self)
        print("Client disconnected: {0}".format(self.peer))

    def lineReceived(self, line):
        # self.factory.communicate(self, payload, isBinary)
        print("Client {0} sending message: {1}".format(self.peer, line))
        self.factory.router[self.peer].command(line.decode())


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
            client.sendLine(payload)
