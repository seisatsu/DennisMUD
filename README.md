# Dennis MUD

Dennis is a MUD (Multi-User Dungeon) inspired by ifMUD in which all content is created by the users, by utilizing in-game commands.

To try it out, make sure you have Python 3, PyMongo, and MongoDB, and then run `cli-frontend.py` for the single-user command-line interface. `irc-frontend.py` hosts the game using an IRC bot as a console that users can message. The IRC backend is not very usable in practice, as it will brush up against anti-flooding protections on most servers. `websocket-backend.py` and `websocket-frontend.html` allow you to set up a webpage as a console.

For each frontend, the example config file needs to be copied and edited. For example, `cli.config.example.json -> cli.config.json`. In the case of the websocket frontend, you will want to modify `websocket-frontend.example.html` to correspond with your backend configuration.
