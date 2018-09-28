# Dennis

This is a MUD (Multi-User Dungeon) in which all content is created by the users, by utilizing in-game commands.

To try it out, make sure you have Python 3, PyMongo, and MongoDB, and then run `cli-frontend.py` for the single-user command-line interface. `irc-frontend.py` hosts the game using an IRC bot as a console that users can message. `websocket-backend.py` and `websocket-frontend.py` allow you to set up a webpage as a console.

For each frontend, the example config file needs to be copied and edited. For example, `cli.config.json.example -> cli.config.json`.
