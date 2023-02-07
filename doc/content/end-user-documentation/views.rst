is_template: False
search_index_weight: 15


.. TODO: rename LonaView to View in 2.0

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

Custom patterns can be any valid regex:

.. code-block:: python

    # routes.py

    from lona import Route

    routes = [
        Route('/<arg1:[a-z]{3}>/', 'views/my_view.py::MyView'),
    ]

It is possible to match any character (including the ``/``).
The following route matches any URL beginning with ``prefix``:

.. code-block:: python

    # routes.py

    from lona import Route

    routes = [
        Route('/prefix<path:.*>', 'views/my_view.py::MyView'),
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

Dictionary Based
````````````````

.. warning::

    Dictionary based responses are deprecated since 1.12 and will be removed
    in 2.0

    Use response classes instead


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

Class Based
```````````

.. note::

    Added in 1.12

.. code-block:: python

    from lona import LonaView, TemplateResponse, TemplateStringResponse


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return TemplateResponse(
                'template_name.html',
                {
                    'variable_name': 'foo',
                },
            )

    class MyLonaView(LonaView):
        def handle_request(self, request):
            return TemplateStringResponse(
                '{{ message }}',
                {
                    'variable_name': 'Template String Response',
                },
            )


Redirects
~~~~~~~~~

Dictionary Based
````````````````

.. warning::

    Dictionary based responses are deprecated since 1.12 and will be removed
    in 2.0

    Use response classes instead


.. code-block:: python

    from lona import LonaView
    from lona.html import H1


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'redirect': '/',
            }


Class Based
```````````

.. note::

    Added in 1.12

.. code-block:: python

    from lona import LonaView, RedirectResponse


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return RedirectResponse('/')


HTTP Redirects
~~~~~~~~~~~~~~

Dictionary Based
````````````````

.. warning::

    Dictionary based responses are deprecated since 1.12 and will be removed
    in 2.0

    Use response classes instead

.. code-block:: python

    from lona import LonaView
    from lona.html import H1


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'http_redirect': '/',
            }

Class Based
```````````

.. note::

    Added in 1.12

.. code-block:: python

    from lona import LonaView, HttpRedirectResponse


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return HttpRedirectResponse('/')


JSON Responses
~~~~~~~~~~~~~~

.. note::

    JSON responses are only available in non interactive views


Dictionary Based
````````````````

.. warning::

    Dictionary based responses are deprecated since 1.12 and will be removed
    in 2.0

    Use response classes instead


.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'json': {
                    'foo': 'bar',
                },
            }

Class Based
```````````

.. note::

    Added in 1.12

.. code-block:: python

    from lona import LonaView, JsonResponse


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return JsonResponse({'foo': 'bar'})


Binary Responses
~~~~~~~~~~~~~~~~

.. note::

    * Binary responses are only available in non interactive views
    * Added in 1.8

Dictionary Based
````````````````

.. warning::

    Dictionary based responses are deprecated since 1.12 and will be removed
    in 2.0

    Use response classes instead

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'content_type': 'application/pdf',
                'body': open('foo.pdf', 'rb').read(),
            }

Class Based
```````````

.. note::

    Added in 1.12

.. code-block:: python

    from lona import LonaView, Response


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return Response(
                content_type='application/pdf',
                body=open('foo.pdf', 'rb').read(),
            )


Custom Headers
~~~~~~~~~~~~~~

.. note::

    * Custom headers are only available in non interactive views
    * Added in 1.8

Dictionary Based
````````````````

.. warning::

    Dictionary based responses are deprecated since 1.12 and will be removed
    in 2.0

    Use response classes instead

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return {
                'headers': {
                    'foo': 'bar',
                },
                'text': 'foo',
            }

Class Based
```````````

.. note::

    Added in 1.12

.. code-block:: python

    from lona import LonaView, Response


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return Response(
                headers={
                    'foo': 'bar',
                },
                text='foo',
            )


View Hooks
----------

.. note::

    * ``LonaView.on_stop()`` was added in 1.7.4
    * ``LonaView.on_cleanup()`` was added in 1.7.4
    * ``LonaView.on_shutdown()`` was removed in 1.8

All entry points for user code in Lona views are callbacks in the ``LonaView``
class. If a hook name starts with ``handle_`` it means that the view can stop
the event handler chain for the incoming event. If a hook name starts with
``on_`` the view gets only notified of the event. It can't control further
handling of the event.

The main entry point of a view is ``handle_request()``. ``handle_request()``
may run indefinitely and wait for events. All other hooks are supposed to run
for shorter periods of time.

After ``handle_request()`` stops, the view stays accessible until the user
closes the tab. That means even after ``handle_request()`` returned, hooks like
``handle_input_event()`` and ``on_view_event()`` are getting called on incoming
events. After ``handle_request()`` stopped, ``on_stop()`` gets called, and
``on_cleanup()`` after the user disconnected, reloaded the tab or changed the
browser URL.

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            return '<h1>Hello World</h1>'

        def handle_input_event_root(self, input_event):
            return input_event

        def handle_input_event(self, input_event):
            return input_event

        def on_view_event(self, view_event):
            pass

        def on_stop(self, reason):
            pass

        def on_cleanup(self):
            pass

        def on_shutdown(self, reason):
            # this hook got removed in 1.8

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


LonaView.on_view_event\(view_event\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This hook gets called for every incoming `view event <#view-events>`_.


LonaView.on_stop\(reason\)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    Added in 1.7.4

This hook gets called after ``handle_request()`` stops. ``reason`` is either
``None`` if ``handle_request()`` finished normally, or an exception if
``handle_request()`` was interrupted or crashed. If it crashed, ``reason``
contains the original exception.

If the ``handle_request()`` was interrupted by the server shutting down,
``reason`` contains a ``lona.exceptions.ServerStop`` exception.

If the ``handle_request()`` was interrupted by the user by closing the
connection, either intentionally or due connection loss, ``reason`` contains
a ``lona.exceptions.UserAbort`` exception.


LonaView.on_cleanup\(\)
~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    Added in 1.7.4

This hook gets called after the view is fully shutdown and gets removed from
the server.


LonaView.on_shutdown\(reason\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    Removed in 1.8

This hook gets called after the view is stopped. The stop reason is ``None``
if the view finished normally or contains a ``lona.exceptions.ServerStop`` or
``lona.exceptions.UserAbort`` if the connected user closed the browser.

It does not run if the view ran into a ``403`` error, a ``500`` error or
returned a response dict.


View Attributes
---------------

.. table::

    ^Name     ^Description
    |server   |Reference to the running Lona server
    |request  |Reference to the request passed into handle_request()


ForbiddenError
--------------

To raise a forbidden error and run the 403 view you can raise
``lona.errors.ForbiddenError``.

**More information:**
`Error views </end-user-documentation/error-views.html>`_

.. code-block:: python

    from lona import LonaView, ForbiddenError


    class MyLonaView(LonaView):
        def handle_request(self, request):
            if not request.user.is_staff:
                raise ForbiddenError

            return '<h1>Hello Admin</h1>'


NotFoundError
-------------

.. note::

    Added in 1.8.3

To raise a not found error and run the 404 view you can raise
``lona.NotFoundError``.

**More information:**
`Error views </end-user-documentation/error-views.html>`_

.. code-block:: python

    import os

    from lona import LonaView, NotFoundError


    class MyLonaView(LonaView):
        def handle_request(self, request):
            path = request.match_info['path']

            if not os.path.exists(path):
                raise NotFoundError

            return {
                'file': path,
            }


Input Events
------------

.. note::

    **Changed in 1.5:** In all versions prior to 1.5, only widgets could handle
    their own events. In versions after 1.5 all node classes can.

    **Changed in 1.7:** In all versions prior to 1.7, ``==`` checked if two
    nodes have equal attributes, but did not check if node A is the same node
    as node B.  To check if node A is node B is ``is`` instead of ``==`` was
    required.

    **Added in 1.7.4:** Redirects

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

Input event handler can also return
`redirects </end-user-documentation/views.html#redirects>`_, even after
`handle_request() </end-user-documentation/views.html#id2>`_ stopped.


Input Event types
~~~~~~~~~~~~~~~~~

CLICK
`````

.. code-block:: python

    from lona.html import HTML, Div, Button, CLICK
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_click(self, input_event):
            print(input_event.tag_name, 'was clicked')

        def handle_request(self, request):
            return HTML(
                Div('Click me', events=[CLICK], handle_click=self.handle_click),

                # Buttons have CLICK set by default
                Button('Click Me', handle_click=self.handle_click),
            )


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
        def handle_change(self, input_event):
            print('TextInput is set to', input_event.node.value)

        def handle_request(self, request):
            return HTML(
                TextInput(value='foo', handle_change=self.handle_change),
            )


FOCUS
`````

.. note::

    Added in 1.9

.. code-block:: python

    from lona.html import HTML, TextInput, FOCUS
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_focus(self, input_event):
            print('TextInput got focused')

        def handle_request(self, request):
            return HTML(
                TextInput(events=[FOCUS], handle_focus=self.handle_focus),
            )


BLUR
````

.. note::

        Added in 1.9

.. code-block:: python

    from lona.html import HTML, TextInput, BLUR
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_blur(self, input_event):
            print('TextInput got blurred')

        def handle_request(self, request):
            return HTML(
                TextInput(events=[BLUR], handle_blur=self.handle_blur),
            )


Input Event Attributes
~~~~~~~~~~~~~~~~~~~~~~

.. note::

    **Added in 1.5:** ``InputEvent.nodes``

    **Added in 1.11:** ``InputEvent.target_node``

.. table::

    ^Name        ^Description
    |node        |(lona.html.Node) Reference to the node that issued the input_event
    |target_node |(lona.html.Node) Reference to the node that that was under the cursor (event.target in JavaScript)
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


Handling Input events In A Callback
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    * Callbacks were Added in 1.5
    * The node keywords ``handle_click`` and ``handle_change`` were added in
      1.6

Every subclass of ``lona.html.AbstractNode`` can implement
``handle_input_event()`` to handle its own input events.

A callbacks can be implemented using inheritance or by simply resetting the
values of ``AbstractNode.handle_input_event()``,
``AbstractNode.handle_click()`` or ``AbstractNode.handle_change()``.

Callbacks can also be set by passing them directly into nodes, using the
``handle_change`` or ``handle_click`` keywords.

.. code-block:: python

    from lona.html import HTML, H1, Button
    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_button_1_click(self, input_event):
            print('button 1 was clicked')

        def handle_button_2_click(self, input_event):
            print('button 2 was clicked')

        def handle_request(self, request):
            button_1 = Button('Button 1')

            button_1.handle_click = self.handle_button_1_click

            html = HTML(
                H1('Click the buttons'),
                button,
                Button('Button 2', handle_click=self.handle_button_2_click),
            )

            self.show(html)


Awaiting Input Events
~~~~~~~~~~~~~~~~~~~~~

Input events can be awaited from ``handle_request()``. This makes forms or
wizards possible.

.. warning::

    Using ``LonaView.await_*`` means that the calling thread blocks until
    the awaited input events gets send by the browser. This is useful when
    writing deamonized views for interactive wizards, but might not scale
    when the user base of your view grows.

    If thread-count and scalability are crucial for you, consider using
    `callbacks </end-user-documentation/views.html#handling-input-events-in-a-callback>`_.

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


Adding Javascript And CSS To View
---------------------------------

.. note::

    Added in 1.7.3

Views can include stylesheets and javascript files in ``STATIC_FILES``.
Such files will be automatically served and included in html.

Static file's ``name`` must be unique in the whole project
(including static files in nodes and widgets).

To control the include order, ``sort_order`` is used. ``sort_order`` is a
simple integer, but to make the code more readable
``lona.static_files.SORT_ORDER`` is used.


.. code-block:: python

    from lona.static_files import StyleSheet, Script, SORT_ORDER
    from lona import LonaView

    class MyView(LonaView):
        STATIC_FILES = [
            # styesheets
            StyleSheet(
                name='chart_css_min',
                path='static/Chart.min.css',
                url='Chart.min.css',
                sort_order=SORT_ORDER.FRAMEWORK,
            ),
            StyleSheet(
                name='chart_css',
                path='static/Chart.css',
                url='Chart.css',
                sort_order=SORT_ORDER.FRAMEWORK,
                link=False,  # When link is set to False the given file
                             # gets collected, but not linked. That's necessary
                             # to make map files possible.
            ),

            # scripts
            Script(
                name='chart_bundle_js_min',
                path='static/Chart.bundle.min.js',
                url='Chart.bundle.min.js',
                sort_order=SORT_ORDER.FRAMEWORK,
            ),
            Script(
                name='chart_bundle_js',
                path='static/Chart.bundle.js',
                url='Chart.bundle.js',
                sort_order=SORT_ORDER.FRAMEWORK,
                link=False,
            ),
            Script(
                name='chart_js_widget_js',
                path='static/chart-js-widget.js',
                url='chart-js-widget.js',
                sort_order=SORT_ORDER.LIBRARY,
            ),
        ]

        def handle_request(self, request):
            return 'SUCCESS'


View Events
-----------

.. note::

    * Added in 1.7.3
    * Redirect support was added in 1.7.4

Views can communicate with each other by sending events using
``LonaView.fire_view_event()``. A view event consists of a name and data.
The name is mandatory and has to be a string, the data is optional but if set
has to be a dict.

When a event is send using ``LonaView.fire_view_event()`` it is send to every
object of the same view class. To send events to multiple view classes
``Server.fire_view_event()`` can be used. Incoming view events are getting
handled by ``LonaView.on_view_event()``.

View event handler can return
`redirects </end-user-documentation/views.html#redirects>`_, even after
`handle_request() </end-user-documentation/views.html#id2>`_ stopped.

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def on_view_event(self, view_event):
            print(view_event.name, view_event.data)

        def handle_request(self, request):
            self.fire_view_event('my-event-name', {'foo': 'bar'})


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

    .. note::

        ``LonaView.await_*`` blocks the current thread until a matching
        event gets send by the browser.

        Read `Awaiting Input Events </end-user-documentation/views.html#awaiting-input-events>`_
        for more information.

    Returns the next incoming input event.

    When ``nodes`` is set, the next input event issued by one of the given
    nodes is returned.

    When ``html`` is set, ``LonaView.show()`` gets called before waiting on
    an input event



LonaView.await_click\(\*nodes, html=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. note::

        ``LonaView.await_*`` blocks the current thread until a matching
        event gets send by the browser.

        Read `Awaiting Input Events </end-user-documentation/views.html#awaiting-input-events>`_
        for more information.

    Returns the next incoming click event.

    When ``nodes`` is set, the next input event issued by one of the given
    nodes is returned.

    When ``html`` is set, ``LonaView.show()`` gets called before waiting on
    an input event


LonaView.await_change\(\*nodes, html=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. note::

        ``LonaView.await_*`` blocks the current thread until a matching
        event gets send by the browser.

        Read `Awaiting Input Events </end-user-documentation/views.html#awaiting-input-events>`_
        for more information.

    Returns the next incoming change event.

    When ``nodes`` is set, the next input event issued by one of the given
    nodes is returned.

    When ``html`` is set, ``LonaView.show()`` gets called before waiting on
    an input event


LonaView.await_focus\(\*nodes, html=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. note::

        Added in 1.9

    .. note::

        ``LonaView.await_*`` blocks the current thread until a matching
        event gets send by the browser.

        Read `Awaiting Input Events </end-user-documentation/views.html#awaiting-input-events>`_
        for more information.

    Returns the next incoming focus event.

    When ``nodes`` is set, the next input event issued by one of the given
    nodes is returned.

    When ``html`` is set, ``LonaView.show()`` gets called before waiting on
    an input event


LonaView.await_blur\(\*nodes, html=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. note::

        Added in 1.9

    .. note::

        ``LonaView.await_*`` blocks the current thread until a matching
        event gets send by the browser.

        Read `Awaiting Input Events </end-user-documentation/views.html#awaiting-input-events>`_
        for more information.

    Returns the next incoming blur event.

    When ``nodes`` is set, the next input event issued by one of the given
    nodes is returned.

    When ``html`` is set, ``LonaView.show()`` gets called before waiting on
    an input event


LonaView.daemonize\(\)
~~~~~~~~~~~~~~~~~~~~~~

    .. warning::

        This method is deprecated and will be removed in Lona 2.0.

        Use ``LonaView.is_daemon`` instead.


    Allow the view to run in background after the user disconnected.

    .. note::

        Daemonized views are not meant to be used to create multi-user views.
        They are meant to create single-user views that are long running
        (multiple minutes or hours).

        For example if you write a view that process a huge amount of data, and
        you want to push a progress bar forward.

        If you want to create multi-user views, use
        `view events </end-user-documentation/views.html?q=view_event#view-events>`_.


LonaView.is_daemon
~~~~~~~~~~~~~~~~~~

    .. note::

        Added in 1.11

    Boolean property. When set to ``True``, the view remains on the server
    after it finished and can be connected and reconnected by one or more
    browsers or browser tabs of the same user.
    The view gets removed from the server after the view explicitly sets
    ``LonaView.is_daemon`` to ``False``.

    .. note::

        In all versions prior to 1.11, daemonized views got removed immediately
        from the server when their ``LonaView.handle_requset()`` returned.
        To maintain compatibility with older code, this new behavior is only
        active if ``LonaView.STOP_DAEMON_WHEN_VIEW_FINISHES`` is set to
        ``False``.


LonaView.iter_objects\(\)
~~~~~~~~~~~~~~~~~~~~~~~~~

    .. note::

        Removed in 1.8

    Returns a generator over all objects of the view class. This is useful
    to build multi user views.


LonaView.fire_view_event\(name, data=None\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. note::

        Added in 1.7.3

    Sends a view event to all objects of its class. ``name`` has to be a
    ``str``, ``data`` is optional but has to be a ``dict`` if set.

    To send a view event to multiple view classes use
    ``Server.fire_view_event()`` instead.



LonaView.send_str\(string, broadcast=False, filter_connections=lambda connection: True, wait=True\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Sends given string over the websocket connection to all clients, connected
    to this view. When broadcast is set, the string gets send to all websocket
    connections connected to the server.

    The filter gets called for every connection that is about to get the string
    send.

    .. code-block:: python

        from lona import LonaView


        class MyLonaView(LonaView):
            def filter_admins(self, connection):
                if connection.user.is_admin:
                    return True

                return False

            def handle_request(self, request):
                self.send_str(
                    'message only for admins',
                    broadcast=True,
                    filter_connections=self.filter_admins,
                )


    The method returns when the message got send. When ``wait`` is set to
    False, the method returns immediately after the string got written to the
    connection message queues.

    **More information:**
    `Sending custom messages </end-user-documentation/frontends.html#sending-custom-messages>`_


LonaView.sleep\(\*\*args, \*\*kwargs\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Calls ``asyncio.sleep()``, but is abortable.

    When using ``asyncio.sleep()`` or ``time.sleep()`` directly, the server
    cannot shutdown til the call returns.

    When using ``LonaView.sleep()`` the Lona server can the abort the call when
    shutting down.


LonaView.ping\(\)
~~~~~~~~~~~~~~~~~

    This method raises a ``lona.exception.UserAbort`` or
    ``lona.exception.ServerStop`` if the server got stopped or the user left.


LonaView.await_sync\(awaitable\)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Takes a asyncio awaitable and schedules it to ``server.loop``. The method
    returns the return value of the ``awaitable``, raises its exception or
    raises ``lona.exception.UserAbort`` or ``lona.exceptions.ServerStop`` if
    the server stopped while waiting on ``awaitable`` or the user left.


LonaView.embed_shell\(\)
~~~~~~~~~~~~~~~~~~~~~~~~

    .. note::

        Removed in 1.8. Use rlpython directly instead.

        .. code-block:: python

            import rlpython
            rlpython.embed()

    Embeds a `rlpython <https://pypi.org/project/rlpython/>`_ based shell.
    More info on shells:
    `Debugging </end-user-documentation/debugging.html>`_.
