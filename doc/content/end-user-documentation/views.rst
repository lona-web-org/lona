is_template: False


Views
=====

View Types
----------

Interactive
~~~~~~~~~~~

By default all Lona views are interactive. Interactive Lona views run over an
websocket connection, which makes input events and background views possible.

**More information:**
`Basic Concept </basic-concept.html>`_


Non-Interactive
~~~~~~~~~~~~~~~

Non interactive views run on HTTP, not websockets. This is useful to add a
JSON-API to your project for example.

To mark a view non interactive, use the ``interactive`` keyword in the
``routes.py``.

.. code-block:: python

    # routes.py

    from lona import Route

    routes = [
        Route('/json-api.json', 'views/json_api.py::JSONAPIView', interactive=False)
    ]

.. code-block:: python

    # views/json_api.py

    from lona import LonaView


    class JSONAPIView(LonaView):
        def handle_request(self, request):
            return {
                'json': {'exit_code': 0, 'value': 'foo'},
            }


HTTP Pass Through
~~~~~~~~~~~~~~~~~

HTTP pass through views bypass the most of the Lona server infrastructure and
speak directly to `aiohttp <https://docs.aiohttp.org/en/stable/>`_. Therefore HTTP
pass through views get `aiohttp request objects <https://docs.aiohttp.org/en/stable/web_reference.html#request-and-base-request>`_
passed in and have to return `aiohttp response objects <https://docs.aiohttp.org/en/stable/web_reference.html#response-classes>`_.

This is useful to use basic HTTP features like file upload, or connect Lona
to WSGI based frameworks like Django.

HTTP pass through views can be callbacks instead of classes, to make
projects like `aiohttp wsgi <https://aiohttp-wsgi.readthedocs.io/en/stable/>`_
work. More information:
`Integrating Django </cookbook/integrating-django.html>`_.

To mark a view as HTTP pass through, use the ``http_pass_through`` keyword in the
``routes.py``.


.. code-block:: python

    # routes.py

    from lona import Route

    routes = [
        Route('/http-pass-through/', 'views/http_pass_through.py::HTTPPassThroughView',
              http_pass_through=True),
    ]


.. code-block:: python

    # views/http_pass_through.py

    from aiohttp.web import Response

    from lona import LonaView


    class HTTPPassThroughView(LonaView):
        def handle_request(self, request):
            return Response(
                body='<h1>HTTP Pass Through</h1>',
                content_type='text/html',
            )


URL Args
--------

Simple Patterns
~~~~~~~~~~~~~~~

.. code-block:: python

    # routes.py

    from lona import Route

    routes = [
        Route('/<arg1>/<arg2>/', 'views/my_view.py::MyView'),
    ]

.. code-block:: python

    # views/my_view.py

    from lona import LonaView


    class MyView(LonaView):
        def handle_request(self, request):
            arg1 = request.match_info['arg1']
            arg2 = request.match_info['arg2']


Custom Patterns
~~~~~~~~~~~~~~~

.. code-block:: python

    # routes.py

    from lona import Route

    routes = [
        Route('/<arg1:[a-z]{3}>/', 'views/my_view.py::MyView'),
    ]


Trailing Slashes
~~~~~~~~~~~~~~~~

.. code-block:: python

    # routes.py

    from lona import Route

    routes = [
        Route('/<arg1>(/)', 'views/my_view.py::MyView'),
    ]


Request Objects
---------------

Attributes
~~~~~~~~~~

.. note::

    * ``request.user`` is writable since 1.4
    * ``request.interactive`` was added in 1.4

.. table::

    ^Name        ^Description
    |interactive |(Bool) Is true when the request came in over an websocket connection
    |method      |(String) Contains either 'GET' or 'POST'
    |GET         |(Dict) Contains the URL query
    |POST        |(Dict) Contains POST arguments. Empty in case of GET requests
    |route       |(lona.routing.Route) Contains the Lona route that linked to this view
    |match_info  |(Dict) Contains the routing Match info
    |user        |Contains the user associated with this request
    |url         |Python yarl url object
    |frontend    |(Bool) flag if this is a frontend view
    |server      |Reference to the running Lona server


GET
~~~

By default all Lona view requests are GET requests. The URL query is stored
in ``request.GET``.

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            print(request.method)
            print(request.GET)

            return ''


POST
~~~~

It is possible to use traditional POST requests. This doesn't require the view
to wait for user input and saves resources.

.. code-block:: python

    from lona.html import HTML, Form, TextInput, Submit, H1
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            if request.method == 'POST':
                return f'<h1>Hello {request.POST["name"]}</h1>'

            return HTML(
                H1('Enter your name'),
                Form(
                    TextInput(name='name'),
                    Submit('Submit'),
                    action='.',
                    method='post',
                ),
            )


Response Objects
----------------

HTML Responses
~~~~~~~~~~~~~~

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return """
                <h1>Hello World</h1>
            """


.. code-block:: python

    from lona import LonaView
    from lona.html import H1


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return H1('Hello World')


Template Responses
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'template': 'path/to/your/template.html',
                'foo': 'bar',
            }


.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'template_string': '<h1>{{ header }}}</h1>',
                'header': 'Hello World',
            }


Redirects
~~~~~~~~~

.. code-block:: python

    from lona import LonaView
    from lona.html import H1


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'redirect': '/',
            }


HTTP Redirects
~~~~~~~~~~~~~~

.. code-block:: python

    from lona import LonaView
    from lona.html import H1


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'http_redirect': '/',
            }


JSON Responses
~~~~~~~~~~~~~~

.. note::

    JSON responses are only available in non interactive views

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'json': {
                    'foo': 'bar',
                },
            }


View Hooks
----------

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return '<h1>Hello World</h1>'

        def handle_input_event_root(self, input_event):
            return input_event

        def handle_input_event(self, input_event):
            return input_event

        def on_shutdown(self, reason):
            pass


LonaView.handle_request\(request\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Gets called with a ``lona.request.Request`` object, and has to return a
response object described in `Response Objects <#response-objects>`_.

``handle_request()`` is the main entry point for every view. Your main logic
should be stored here.


LonaView.handle_input_event_root\(input_event\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This hook is gets called first for every input event and is able to override
all input event behavior.

This hook is required to return the given input event or ``None``. If the input
event is returned, the chain of input events described in
`Input Events <#id2>`_ continues. If the return value is ``None`` Lona
regards the input event as handled and aborts the chain.


LonaView.handle_input_event\(input_event\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This hook is gets called for every input event that is not awaited in
``handle_request()`` or handled by a widget.


LonaView.on_shutdown\(reason\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This hook gets called after the view is stopped. The stop reason is ``None``
if the view finished normally or contains a ``lona.exceptions.ServerStop`` or
``lona.exceptions.UserAbort`` if the connected user closed the browser.


View Attributes
---------------

.. table::

    ^Name     ^Description
    |server   |Reference to the running Lona server
    |request  |Reference to the request passed into handle_request()


Authentication
--------------

To raise a forbidden error and run the 403 view you can raise
``lona.errors.ForbiddenError``.

**More information:**
`Error views </end-user-documentation/error-views.html>`_

.. code-block:: python

    from lona.errors import ForbiddenError
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            if not request.user.is_staff:
                raise forbidden

            return '<h1>Hello Admin</h1>'



Input Events
------------

.. note::

    Changed in 1.5: In all versions prior to 1.5, only widgets could handle
    their own events. In versions after 1.5 all node classes can.

Input events get handled in a chain of hooks. Every hook is required to return
the given input event, to pass it down the chain, or return ``None`` to mark
the event as handled.

The first member of the chain is ``LonaView.handle_input_event_root()``. If the
event got returned Lona passes the event into all
``AbstractNode.handle_input_event()`` by bubbling the event the HTML tree up.
If the event got returned by the last widget in the chain, Lona checks if
``LonaView.handle_request()`` awaits an input event using
``await_[input_event|click|change]()``. If not
``LonaView.handle_input_event()`` gets called as last member of the chain.

Input events can, but don't have to, contain a node that issued the event in
``input_event.node``.

.. note::

    Be careful when comparing ``input_event.node`` with another node.
    ``==`` checks if two nodes have equal attributes, bot does not check if
    node A is the same node as node B.

    To check if node A is node B us ``is`` instead of ``==``.


Input Event types
~~~~~~~~~~~~~~~~~

CLICK
`````

.. code-block:: python

    from lona.html import HTML, Div, Button, CLICK
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            html = HTML(
                Div('Click me', events=[CLICK]),
                Button('Click Me'),  # Buttons have CLICK set by default
            )

            while True:
                self.show(html)
                input_event = self.await_click()

                print(input_event.tag_name, 'was clicked')


Click events contain meta data in ``input_event.data``.

.. table::

    ^Name         ^Description
    |alt_key      |Boolean. Is True when ALT was pressed while clicking
    |ctrl_key     |Boolean. Is True when CTRL was pressed while clicking
    |shift_key    |Boolean. Is True when SHIFT was pressed while clicking
    |meta_key     |Boolean. Is True when META was pressed while clicking
    |node_height  |Integer. Contains the height of the clicked node
    |node_width   |Integer. Contains the width of the clicked node
    |x            |Integer. Contains the x coordinate of the Cursor
    |y            |Integer. Contains the y coordinate of the Cursor


CHANGE
``````

.. code-block:: python

    from lona.html import HTML, TextInput
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            html = HTML(
                TextInput(value='foo', bubble_up=True),
            )

            while True:
                self.show(html)
                input_event = self.await_change()

                print('TextInput is set to', input_event.node.value)


Input Event Attributes
~~~~~~~~~~~~~~~~~~~~~~

.. note::

    Added in 1.5: ``InputEvent.nodes``

.. table::

    ^Name        ^Description
    |node        |(lona.html.Node) Reference to the node that issued the input_event
    |nodes       |(list(lona.html.Node)) Contains a list of all nodes in the chain up to the root
    |data        |(Dict) For click events this contains meta data from the browser
    |tag_name    |(String) Contains the tag name of the node in the browser
    |id_list     |(List) Contains a list of all ids of the node in the browser
    |class_list  |(List) Contains a list of all classes of the node in the browser
    |event_id    |(Int) Contains the event id
    |connection  |(lona.connection.Connection) Contains the connection over that this event came in
    |window_id   |The window id the browser gave this view
    |request     |(lona.request.Request) Contains the request over that this event came in
    |document    |(lona.html.document.Document) Contains the document that contains input_event.node
    |payload     |(List) Contains the raw event payload


Input Event Methods
~~~~~~~~~~~~~~~~~~~

InputEvent.node_has_id(name)
````````````````````````````

    Returnes ``True`` if the node associated with this event has the given id.


InputEvent.node_has_class(name)
```````````````````````````````

    Returnes ``True`` if the node associated with this event has the given class.


Awaiting Input Events
~~~~~~~~~~~~~~~~~~~~~

Input events can be awaited from ``handle_request()``. This makes forms or
wizards possible.

.. code-block:: python

    from lona.html import HTML, H1, Button
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            html = HTML(
                H1('Click the button'),
                Button('click me'),
            )

            self.show(html)

            input_event = self.await_click()

            print(input_event.node, 'was clicked')


Handling Input events In A Callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    Added in 1.5

Every subclass of ``lona.html.AbstractNode`` can implement
``handle_input_event()`` to handle its own input events.

A callbacks can be implemented using inheritance or by simply resetting the
values of ``AbstractNode.handle_input_event()``,
``AbstractNode.handle_click()`` or ``AbstractNode.handle_change()``.

.. code-block:: python

    from lona.html import HTML, H1, Button
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_button_click(self, input_event):
            print('button was clicked')

        def handle_request(self, request):
            button = Button('click me')

            button.handle_click = self.handle_button_click

            html = HTML(
                H1('Click the button'),
                button,
            )

            self.show(html)


Handling Input Events In A Hook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Input events can also be handled in ``handle_input_event()`` when
``handle_request()`` is busy.

.. code-block:: python

    from datetime import datetime

    from lona.html import HTML, H1, Div, Button
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            self.timestamp = Div()
            self.message = Div()
            self.button = Button('click me')

            self.html = HTML(
                H1('Click the button'),
                self.timestamp,
                self.message,
            )

            while True:
                timestamp.set_text(str(datetime.now()))

                self.show(self.html)

                self.sleep(1)

        def handle_input_event(self, input_event):
            if not input_event.node == self.button:
                return input_event

            self.message.set_text(f'Button was clicked at {datetime.now()}')


Overriding All Input Event Hooks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``handle_input_event_root()`` gets always called first. This makes it possible
to override even widget event handler.

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_input_event_root(self, input_event):
            print(input_event)


View Methods
------------

LonaView.show\(html=None, template=None, template_string=None, title=None, template_context=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. note::

        This method works in interactive mode only

    Takes a HTML tree from ``lona.html``, a string or a template name and context
    and sends it to the client.

    When the given html is a HTML tree and it is the same object as the in call
    before, Lona sends only updates, not the entire HTML tree all over again.

    **More information on HTML trees:**
    `HTML </end-user-documentation/html.html>`_


LonaView.set_title(title)
~~~~~~~~~~~~~~~~~~~~~~~~~

    .. note::

        This method works in interactive mode only

    This method sets the title of the browser tab.


LonaView.await_input_event\(\*nodes, html=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes the next incoming input event.

    When ``nodes`` is set, the next input event issued by one of the given
    nodes is returned.

    When ``html`` is set, ``LonaView.show()`` gets called before waiting on
    an input event


LonaView.await_click\(\*nodes, html=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes the next incoming click event.

    When ``nodes`` is set, the next input event issued by one of the given
    nodes is returned.

    When ``html`` is set, ``LonaView.show()`` gets called before waiting on
    an input event


LonaView.await_change\(\*nodes, html=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes the next incoming change event.

    When ``nodes`` is set, the next input event issued by one of the given
    nodes is returned.

    When ``html`` is set, ``LonaView.show()`` gets called before waiting on
    an input event


LonaView.daemonize\(\)
~~~~~~~~~~~~~~~~~~~~~~

    Allow the view to run in background after the user disconnected.


LonaView.iter_objects\(\)
~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes a generator over all objects of the view class. This is useful
    to build multi user views.


LonaView.send_str\(string, broadcast=False, filter_connections=lambda connection: True, wait=True\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sends given string over the websocket connection to all clients, connected
    to this view. When broadcast is set, the string gets send to all websocket
    connections connected to the server.

    The filter gets called for every connection that is about to get the string
    send.

    .. code-block:: python

        def filter_admins(connection):
            if connection.user.is_admin:
                return True

            return False

        send_str('message only for admins', broadcast=True, filter_connections=filter_admins)

    The method returns when the message got send. When ``wait`` is set to
    False, the method returnes immediately after the string got written to the
    connection message queues.

    **More information:**
    `Sending custom messages </end-user-documentation/frontends.html#sending-custom-messages>`_


LonaView.sleep\(\*\*args, \*\*kwargs\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Calls ``asyncio.sleep()``, but is abortable.

    When using ``asyncio.sleep()`` or ``time.sleep()`` directly, the server
    cannot shutdown til the call returnes.

    When using ``LonaView.sleep()`` the Lona server can the abort the call when
    shutting down.


LonaView.ping\(\)
~~~~~~~~~~~~~~~~~

    This method raises a ``lona.exception.UserAbort`` or
    ``lona.exception.ServerStop`` if the server got stopped or the user left.


LonaView.await_sync\(awaitable\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Takes a asyncio awaitable and schedules it to ``server.loop``. The method
    returnes the return value of the ``awaitable``, raises its exception or
    raises ``lona.exception.UserAbort`` or ``lona.exceptions.ServerStop`` if
    the server stopped while waiting on ``awaitable`` or the user left.


LonaView.embed_shell\(\)
~~~~~~~~~~~~~~~~~~~~~~~~

    Embeds a `rlpython <https://pypi.org/project/rlpython/>`_ based shell.
    More info on shells:
    `Debugging </end-user-documentation/debugging.html>`_.


Server Methods
--------------

Server.get_running_views_count\(user\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes the count of running views for the given user as integer.


Server.view_is_already_running\(request\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes if a view for the given request is already running as boolean.


Server.get_connection_count\(user\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes the count of connections for the given user as integer.


Server.get_connected_user_count\(\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes the count of connected users as integer.


Server.get_template\(template_name\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes a Jinja2 template object associated with the given template name


Server.render_string\(template_string, \*\*template_context\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes a rendered Jinja2 template string as string.


Server.render_template\(template_name, \*\*template_context\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes a rendered Jinja2 template as string.


Server.get_view_class\(route=None, import_string=None, url=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes the ``lona.view.LonaView`` subclass associated with the given
    route, import string or url.

    Only one argument can be set at a time.


Server.reverse\(url_name, \*\*url_args\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Returnes a routing reverse match as string.


Server.embed_shell\(\)
~~~~~~~~~~~~~~~~~~~~~~

    Embeds a `rlpython <https://pypi.org/project/rlpython/>`_ based shell in
    the server context.
    More info on shells:
    `Debugging </end-user-documentation/debugging.html>`_.
