search_index_weight: 10


Frequently Asked Questions
==========================

Why all the effort? What problem are you trying to solve here?
--------------------------------------------------------------

**fscherf:** I am a full stack developer and have no problems writing big
applications using Python, Javascript, HTML and CSS, juggling multiple
techniques and frameworks at the same time. Also i am very experienced with
async code and asyncio. But at work i am the only one with this skill set. The
most of the other developers have application specific domain knowledge but can
write Python code.

One of our biggest internal projects at work is a web based accounting
system. If there is a bug that is not a technical, but an accounting issue, i
can't do anything about it (i have no clue about accounting). If the bug
touches multiple layers of the software (backend and frontend) our application
developers are sometimes busy for days. Thats slows down development and that's
expensive.

With Lona, and the Lona widgets i created for the accounting system, i can give
them a very simple, abstract and pythonic API for common
tasks like "show an table and then update it", "show a progressbar with an
abort button" or "show a popup with 3 buttons". The code is more readable for
everyone involved, and the application developers can solve most of their
problems on their own now.

Lona may have some performance disadvantages over React for example, but
CPU-time is cheap these days, developer-time is expensive!


Since all events get sent to the server and get handled in Python, how high is the latency?
-------------------------------------------------------------------------------------------

**fscherf:** Because all state has to go through network back an forth there is
some latency. But you would have this kind of latency anyway, when you have to
access server state, what most applications do at some point. In the kind of
projects i work on, all interesting state is on the server, and it makes more
sense to make decisions, like if a button is clickable or not, there.

There are cases where it makes more sense to handle events in Javascript
directly, because they fire very often per second or have sensitive timing
constrains. In this case you can add a
`Frontend Widget </api-reference/html.html#frontend-widgets>`_
which can contain some Javascript code, to handle your events directly in the
browser.

I have no real latency measurements but this was never a problem.
If your application has very sensitive timing constrains Lona will be the wrong
tool. For "normal" interaction, the latency is not noticeable.

To notice latencies the Lona Javascript client defines some
`Hooks </api-reference/frontends.html#view-start-timeout>`_. These
can be used to inform the user or the admin that the server is slow.


How does Lona perform compared with React, Vue or Angular?
----------------------------------------------------------

**fscherf:** Lona is not meant to compete with React, Vue or Angular or to be
used by a startup to create the next Amazon or Netflix. Lona is meant for
projects where previously the alternative was to have no web interface at all.

A coworker of mine created a small python script that generates qr-codes for a
small label printer. He is from the hardware team, so there is no way he would
bother to create a web interface using React or something else, but with Lona
he had to add ~20 lines of extra Python code.

Web is a very powerful tool for visualization and interaction. Python is a
powerful tool for an unlimited range of tasks. Lona tries to bridge this gap
and is designed to be very accessible and good for rapid prototyping.


Why has Lona no live-reload feature like aiohttp-devtools?
----------------------------------------------------------

**fscherf:** Early versions of Lona had such a feature, but it got removed due
bad user experience: Reloading your view helps when the view is fully self
contained, but when it uses widgets or helper functions from another module,
things become inconsistent.

To make that a reliable feature you would have to maintain a list of all loaded
files and directories and track changes, file removes and addition of new
files. And you would have to maintain this list between restarts, to not miss
events, if files get changed fast after each other, like in a git rebase.

Also people use different editors that save files at different times and
sometimes multiple times and/or periodically.

Its hard to get this right, therefore i focused on making the server fast to
restart and easier to maintain.
