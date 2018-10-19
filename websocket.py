#####################
# Dennis MUD        #
# websocket.py      #
# Copyright 2018    #
# Michael D. Reiley #
#####################

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

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol


class ServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        self.factory.register(self)
        print("Client connected: {0}".format(self.peer))

    def connectionLost(self, reason):
        self.factory.unregister(self)
        print("Client disconnected: {0}".format(self.peer))

    def onMessage(self, payload, isBinary):
        # self.factory.communicate(self, payload, isBinary)
        print("Client {0} sending message: {1}".format(self.peer, payload))
        # Error handling and reporting.
        try:
            self.factory.router[self.peer][1].command(payload.decode('utf-8'))
        except:
            self.factory.communicate(self.peer, traceback.format_exc().encode('utf-8'))


class ServerFactory(WebSocketServerFactory):

    def __init__(self, router, *args, **kwargs):
        self.router = router
        self.router.websocket_factory = self
        super(ServerFactory, self).__init__(*args)
        self.clients = []

    def register(self, client):
        self.clients.append({'client-peer': client.peer, 'client': client})
        self.router.register(client.peer, "websocket")

    def unregister(self, client):
        self.router.unregister(client.peer)
        for c in self.clients:
            if c['client-peer'] == client.peer:
                self.clients.remove(c)

    def communicate(self, peer, payload, _nbsp=False):
        client = None
        for c in self.clients:
            if c['client-peer'] == peer:
                client = c['client']
        if client:
            message = payload.decode('utf-8').replace("\n", "<br/>")
            if _nbsp:
                message = message.replace(" ", "&nbsp;")
            message = message.encode('utf-8')
            client.sendMessage(message)

