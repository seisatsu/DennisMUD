# Dennis MUD

Dennis is a MUD (Multi-User Dungeon) inspired by ifMUD in which all content is created by the users, by utilizing in-game commands.

A public test instance is generally kept running. Access it with the web client at http://dennis.seisat.su/ or via telnet at `dennis.seisat.su:37381`.

To try it out, make sure you have Python 3, PyMongo, and MongoDB, and then copy `cli.config.example.json` to `cli.config.json` and  run `cli-frontend.py` for the single-user command-line interface.

To run as a server, you can run `server.py`, which supports telnet and websocket. `websocket-frontend.example.html` provides an example client for the websocket service. You will also have to copy `server.config.example.json` to `server.config.json`.
