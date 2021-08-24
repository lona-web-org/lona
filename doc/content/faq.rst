

Frequently Asked Questions
==========================

Why has Lona no live-reload feature like aiohttp-devtools?
----------------------------------------------------------

**fscherf:** Early versions of Lona had such a feature, but it got removed due
bad user experience: Reloading your view helps when the view is fully self
contained, but when it uses widgets or helper functions from another module,
things become inconsistent.

To make that a reliable feature you would have to maintain a list of all loaded
files and directories, and track changes, file removes and addition of new
files. And you would have to maintain this list between restarts, to not miss
events, if files get changed fast after each other, like in a git rebase.

Also people use different editors that save files at different times and
sometimes multiple times and/or periodically.

Its hard to get this right, therefore i focused on making the server fast to
restart and easier to maintain.