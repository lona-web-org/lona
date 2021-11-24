search_index_weight: 15


Lona Scripts
============

For microservices or small prototypes Lona apps can be run using a single
python script.

.. code-block:: text

    $ pip install lona

.. code-block:: python

    from datetime import datetime

    from lona.html import HTML, H1, Div
    from lona import LonaApp, LonaView

    app = LonaApp(__file__)


    @app.route('/')
    class ClockView(LonaView):
        def handle_request(self, request):
            timestamp = Div()

            html = HTML(
                H1('Clock'),
                timestamp,
            )

            while True:
                timestamp.set_text(str(datetime.now()))

                self.show(html)

                self.sleep(1)


    app.run()


Command Line Arguments
----------------------

.. note::

    ``--syslog-priorities`` and ``syslog_priorities`` were added in 1.8.3

``LonaApp.run()`` supports command line arguments, like
`Lona Server </end-user-documentation/debugging.html#lona-server-command-line-options>`_,
to make calls like ``python your-script.py --port=8081`` work.

.. table::

    ^Option               ^Description
    |-l / --log-level     |Set log level to [debug,info,warn,error,critical]
    |--loggers            |Enable or disable a given list of loggers <br> To include a logger use "+{LOGGER_NAME}", to exclude "_{LOGGER_NAME}"
    |--debug-mode         |Enable debug log for {messages,views,input-events,view-events}
    |--syslog-priorities  |Adds syslog priorities to log [no,auto,always] (auto is default)
    |--shell              |Embed a shell in the same process as the server
    |--shell-server       |Starts rlpython shell server containing a Lona shell <br> More Information: <a href="#lona-shell">Lona Shell</a>
    |-o                   |Set setting to value before settings.py got loaded <br> example "-o MY_FEATURE=True"
    |-O                   |Set setting to value after settings.py got loaded <br> example "-o MY_FEATURE=True"


LonaApp.run\(\) Arguments
-------------------------

.. table::

    ^Name               ^Default      ^Description
    |host               |'localhost' |(Str) Host to bind against
    |port               |8080        |(Int) Port to bind against
    |log_level          |'info'      |(Str) Set log level to [debug,info,warn,error,critical]
    |loggers            |[]          |(List) Enable or disable a given list of loggers <br> To include a logger use "+{LOGGER_NAME}", <br> to exclude "_{LOGGER_NAME}"
    |debug_mode         |''          |(Str) Enable debug log for {messages,views,input-events}
    |syslog_priorities  |'auto'      |(Str) Adds syslog priorities to log [no,auto,always]
    |shutdown_timeout   |0           |(Int) aiohttp server shutdown timeout
    |shell              |False       |(Bool) Embed a shell in the same process as the server
    |shell_server_url   |''          |(Str) Lona Shell Server URL<br>More information: <a href="/end-user-documentation/debugging.html#lona-shell">Lona Shell</a>


Settings
--------

A Lona settings object is a available in ``LonaApp.settings``.

**More Information:**
{{ link('end-user-documentation/settings.rst', 'Settings') }}

.. code-block:: python

    from lona import LonaApp

    app = LonaApp(__file__)

    app.settings.MAX_WORKER_THREADS = 10


Adding Views
------------

Views can be added by using the ``LonaApp.route()`` decorator or by setting
``LonaApp.routes`` to a list of ``lona.routing.Route`` objects directly.

``LonaApp.route()`` takes the same arguments like ``lona.routing.Route``.

**More information:**
{{ link('end-user-documentation/views.rst', 'Views') }}

.. code-block:: python

    from lona import LonaApp, LonaView
    from lona.html import H1

    app = LonaApp(__file__)


    @app.route('/')
    class MyLonaView(LonaView):
        def handle_request(self, request):
            return H1('Hello World')


    app.run()


Setting The Frontend View
-------------------------

The frontend view can be set by using ``LonaApp.settings.FRONTEND_VIEW`` or
by using the ``LonaApp.frontend_view()`` decorator.

**More information:**
`Writing A Custom Frontend </end-user-documentation/frontends.html#writing-a-custom-frontend-view>`_

.. code-block:: python

    from lona import LonaApp, LonaView

    app = LonaApp(__file__)


    @app.frontend_view
    class MyFrontendView(LonaView):
        def handle_request(self, request):
            return {
                'template': self.server.settings.FRONTEND_TEMPLATE,
            }


Adding Middlewares
------------------

Middlewares can be added by using the ``LonaApp.middleware()`` decorator or by
setting ``LonaApp.settings.MIDDLEWARES`` to a list of middleware classes
or import strings.

**More information:**
{{ link('end-user-documentation/middlewares.rst', 'Middlewares') }}

.. code-block:: python

    from lona import LonaApp

    app = LonaApp(__file__)


    @app.middleware
    class MyMiddleware:
        def handle_request(self, data):
            print('>>', data)

            return data


Adding Templates
----------------

Templates can be added by adding template directory paths to
``LonaApp.settings.TEMPLATE_DIRS`` or by using the ``LonaApp.add_template()``
method.

All paths, besides paths starting with ``/``, have to be relative to the python
script.

**More information on extending the frontend template:**
`Custom Templates </end-user-documentation/frontends.html#custom-templates>`_

.. code-block:: python

    from lona import LonaApp

    app = LonaApp(__file__)

    app.add_template('lona/header.html', """
        <h1>My Lona Project</h1.>
    """)

    app.add_template('lona/header.html', path='lona/header.html')


Adding Static Files
-------------------

Static files can be added by adding static directory paths to
``LonaApp.settings.STATIC_DIRS`` or by using the ``LonaApp.add_static_file()``
method.

All paths, besides paths starting with ``/``, have to be relative to the python
script.

The default frontend template includes ``lona/style.css`` which can be
overridden.

.. code-block:: python

    from lona import LonaApp

    app = LonaApp(__file__)

    app.add_static_file('lona/style.css', """
        body {
            background-color: white;
        }
    """)

    app.add_template('lona/style.css', path='lona/style.css')


Custom Error Views
------------------

.. note::

    Added in 1.8.3

Custom error views can be set using the decorators ``LonaApp.error_403_view``,
``LonaApp.error_404_view`` and ``LonaApp.error_500_view``.

**More information on error views:**
`Error Views </end-user-documentation/error-views.html>`_

.. code-block:: python

    from lona import LonaApp, LonaView

    app = LonaApp(__file__)


    @app.error_403_view
    class Error403View(LonaView):
        def handle_request(self, request, exception):
            return '403: Forbidden'


    @app.error_404_view
    class Error404View(LonaView):
        def handle_request(self, request):
            return '404: Not Found'


    @app.error_500_view
    class Error500View(LonaView):
        def handle_request(self, request, exception):
            return '500: Internal Error'


    app.run()
