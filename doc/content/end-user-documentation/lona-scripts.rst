

Lona Scripts
============

For microservices or small prototypes Lona apps can be run using a single
python script.

.. code-block:: text

    $ pip install lona

.. code-block:: python

    from datetime import datetime
    import time

    from lona.html import HTML, H1, Div
    from lona.view import LonaView
    from lona import LonaApp

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

                time.sleep(1)

    app.run(port=8080)


LonaApp.run\(\) Arguments
-------------------------

.. table::

    ^Name             ^Default      ^Description
    |host             |'localhost' |(Str) Host to bind against
    |port             |8080        |(Int) Port to bind against
    |log_level        |'info'      |(Str) Set log level to [debug,info,warn,error,critical]
    |loggers          |[]          |(List) Enable or disable a given list of loggers <br> To include a logger use "+{LOGGER_NAME}", <br> to exclude "_{LOGGER_NAME}"
    |debug_mode       |''          |(Str) Enable debug log for {messages,views,input-events}
    |shutdown_timeout |0           |(Int) aiohttp server shutdown timeout
    |shell            |False       |(Bool) Embed a shell in the same process as the server
    |shell_server_url |''          |(Str) Lona Shell Server URL<br>More information: <a href="/end-user-documentation/debugging.html#lona-shell">Lona Shell</a>


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

    from lona.view import LonaView
    from lona.html import H1
    from lona import LonaApp

    app = LonaApp(__file__)

    @app.route('/')
    class MyLonaView(LonaView):
        return H1('Hello World')


    app.run()


Setting The Frontend View
-------------------------

The frontend view can be set by using ``LonaApp.settings.FRONTEND_VIEW`` or
by using the ``LonaApp.frontend_view()`` decorator.

**More information:**
`Writing A Custom Frontend </end-user-documentation/frontends.html#writing-a-custom-frontend-view>`_

.. code-block:: python

    from lona.view import LonaView
    from lona import LonaApp

    app = LonaApp(__file__)

    @app.frontend_view
    class MyFrontendView(LonaView):
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

.. code-block:: python

    from lona import LonaApp

    app = LonaApp(__file__)

    app.add_template('my/html/template.html', """
        <h1>My Template</h1.>
        <p>Hello World</p>
    """)

    app.add_template('my/html/template.html', path='path/to/my/template.html')


Adding Static Files
-------------------

Static files can be added by adding static directory paths to
``LonaApp.settings.STATIC_DIRS`` or by using the ``LonaApp.add_static_file()``
method.

All paths, besides paths starting with ``/``, have to be relative to the python
script.

.. code-block:: python

    from lona import LonaApp

    app = LonaApp(__file__)

    app.add_static_file('my/css/stylesheet.css', """
        body {
            background-color: white;
        }
    """)

    app.add_template('my/css/stylesheet.css', path='path/to/my/stylesheet.css')
