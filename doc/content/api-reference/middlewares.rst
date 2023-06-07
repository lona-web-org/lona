search_index_weight: 10


Middlewares
===========

Lona middlewares control connection handling, request handling, websocket
messages and get called on server start and shutdown.

Besides ``on_startup()`` and ``on_shutdown()`` middlewares work like input
event handlers: The middleware data gets passed into every middleware until
the data does not get returned. When the data does not get returned, Lona regards the
data as handled.

Middlewares can be live analyzed by using the
{{ link('api-reference/lona-shell.rst', 'Lona Shell') }} command
``%lona_middlewares``.

.. code-block:: python

    # middlewares/my_middleware.py

    class MyMiddleware:
        async def on_startup(self, data):
            server = data.server

            return data

        async def on_shutdown(self, data):
            server = data.server

            return data

        def handle_http_request(self, data):
            server = data.server
            http_request = data.http_request

            return data

        def handle_connection(self, data):
            server = data.server
            http_request = data.http_request
            connection = data.connection

            return data

        def handle_websocket_message(self, data):
            server = data.server
            connection = data.connection
            message = data.message

            return data

        def handle_request(self, data):
            server = data.server
            connection = data.connection
            request = data.request
            view = data.view

            return data

.. code-block:: python

    # settings.py

    MIDDLEWARES = [
        'middlewares/my_middleware.py::MyMiddleware'
    ]


Middleware.on_startup\(data\)
-----------------------------

.. note::

    This hook has to be a coroutine

Gets called on server start.


Middleware.on_shutdown\(data\)
------------------------------

.. note::

    This hook has to be a coroutine

Gets called on server shutdown.


Middleware.handle_http_request\(data\)
--------------------------------------

Gets called with every incomming HTTP request, before any other routing or
handling happens. If ``data`` is not returned, Lona regards
``data.http_request`` as handled.


Middleware.handle_connection\(data\)
------------------------------------

Gets called with every new connection that is made. If data is not returned,
the connection gets dropped and a 503 error gets sent.


Middleware.handle_websocket_message\(data\)
-------------------------------------------

Gets called for every websocket message that is received.


Middleware.handle_request\(data\)
---------------------------------

Gets called for every request is made by any user.

If the data gets returned, the view associated with this request gets started.

If a `Response Object </api-reference/views.html#response-objects>`_
is returned, the view gets not started and the user gets the returned response
object shown.
