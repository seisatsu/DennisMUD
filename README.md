# Dennis MUD

Dennis is a MUD (Multi-User Dungeon) and collaborative writing exercise inspired by ifMUD in which all content is created by the users, by utilizing in-game commands.

A public test instance is generally kept running. Access it with the web client at http://dennis.seisat.su/ or via telnet at the same host on port 37381.

Single-player
=============

To try out single-player mode on the command line, make sure you have Python 3, PyMongo, and MongoDB, and then copy `cli.config.example.json` to `cli.config.json`, change any necessary settings, and  run `cli-frontend.py`.

Multi-player
============

To run a multi-player server, you can run `server.py`, which will start a websocket and a telnet service by default. `websocket-frontend.example.html` provides an example in-browser client for the websocket service. You will also have to copy `server.config.example.json` to `server.config.json` and change any necessary settings. To run the services, you will need Twisted and Autobahn for Python 3.
