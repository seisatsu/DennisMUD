# Dennis MUD

Dennis is a MUD (Multi-User Dungeon, aka a multi-player text adventure) and collaborative writing exercise inspired by [ifMUD](http://ifmud.port4000.com/), in which all content is created by the users, by utilizing in-game commands. The game starts with a single empty room, and one or more players build a world from that point by adding rooms, exits, and items, and describing them. The in-game `help` command provides a categorized listing and usage instructions for every command in the game. This is an experimental project in early-to-mid alpha, and new features are added frequently.

A public test instance is generally kept running. Access it with the web client at http://dennis.seisat.su/ or via telnet at the same host on port 37381.

Defaults Configuration
======================

There is a configuration file `defaults.config.example.json` which contains a number of default values to use when creating new in-game rooms, items, and users. It is necessary before running Dennis to copy this file to `defaults.config.json`, and make changes if desired.

Single-player
=============

To try out single-player mode on the command line, first make sure you have [Python 3](https://www.python.org/), [PyMongo](https://api.mongodb.com/python/current/), and [MongoDB](https://www.mongodb.com/). Then copy `cli.config.example.json` to `cli.config.json`, change any necessary settings, and  run `python3 cli-frontend.py` in the project's top directory from your console.

Multi-player
============

To run a multi-player server, you can run `server.py`, which will start a websocket service and a telnet service by default. `websocket-frontend.example.html` provides an example in-browser client for the websocket service. You will also have to copy `server.config.example.json` to `server.config.json` and change any necessary settings. To run the services, you will need [Twisted](https://twistedmatrix.com/trac/) and [Autobahn](https://crossbar.io/autobahn/) for Python 3.
