# Dennis MUD - Multiplayer Text Adventure Sandbox

Dennis is a MUD (Multi-User Dungeon, aka a multi-player text adventure) and collaborative writing exercise inspired by [ifMUD](http://ifmud.port4000.com/), in which all content is created by the users, by utilizing in-game commands. The game starts with a single empty room, and one or more players build a world from that point by adding rooms, exits, and items, and assigning them descriptions and attributes. The in-game `help` command provides a categorized listing and usage instructions for every command in the game. This is an experimental project in early alpha, and new features are added frequently. Bugs and backwards-incompatible updates are to be expected.

A public test instance is generally kept running. Access it with the web client at http://play.dennismud.xyz/ or via telnet at the same host on port 37380.

Defaults Configuration
======================

There is a configuration file `defaults.config.example.json` which contains a number of default values to use when creating new in-game rooms, items, and users. It is necessary before running Dennis to copy this file to `defaults.config.json`, and make changes if desired.

Single User Mode (Single-player)
================================

To try out single user mode on the command line, first make sure you have [Python 3](https://www.python.org/), [TinyDB](https://tinydb.readthedocs.io/en/latest/), [Python Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/en/master/), and [jsonschema](https://python-jsonschema.readthedocs.io/en/stable/). (Previous versions used MongoDB.) Then copy `singleuser.config.example.json` to `singleuser.config.json`, change any necessary settings, and  run `python3 singleuser.py` in the project's top directory from your console.

Multi-player Server
===================

To run a multi-player server, you can run `server.py`, which will start a websocket service and a telnet service by default. `websocket-client.example.html` provides an example in-browser client for the websocket service. You will also have to copy `server.config.example.json` to `server.config.json` and change any necessary settings. If you would like, you can also copy `motd.telnet.example.txt` to `motd.telnet.txt` and modify it as needed to provide a message to telnet users upon connection. To run the services, you will need [Python 3](https://www.python.org/), [TinyDB](https://tinydb.readthedocs.io/en/latest/), [jsonschema](https://python-jsonschema.readthedocs.io/en/stable/), [Twisted](https://twistedmatrix.com/trac/), [Autobahn](https://crossbar.io/autobahn/), [pyOpenSSL](https://www.pyopenssl.org/en/stable/), and [service_identity](https://service-identity.readthedocs.io/en/stable/installation.html).

Windows Releases
================

The Windows releases contain binaries which already contain all of the requirements for running the server and cli. You shouldn't need to install anything. You also don't need to copy or rename the config files if you download a Windows release.
