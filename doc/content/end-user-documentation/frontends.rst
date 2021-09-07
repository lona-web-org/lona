is_template: False


Frontends
=========

Interactive views need a frontend view to run before them. The frontend view
is supposed to load the Lona Javascript client, define the basic layout of the
website and load all static files.

**More information:**
`Basic Concept </basic-concept.html>`_


Lona has a default frontend view build in that uses an overrideable template.
To customize your Lona application you can override the template or the entire
view.


Custom Templates
----------------

Lona uses ``settings.FRONTEND_TEMPLATE`` which is set to
``lona/frontend.html`` by default. You can reset this value or provide a
template under this path.

The default frontend template (shown below) is split up in
``lona/header.html``, ``lona/footer.html`` and ``lona/frontend.js``.
Therefore the parts before and after the views can be overridden for styling
and Javascript can be added to ``lona/frontend.js``.

The default frontend template includes ``lona/style.css`` which can be
overridden.

.. code-block:: html

    <!-- templates/lona/frontend.html -->
    <html>
        <head>
            <meta charset="utf-8" />
            {{ Lona.load_stylesheets() }}
            <link href="{{ Lona.load_static_file('lona/style.css') }}" rel="stylesheet">
        </head>
        <body>
            {% include "lona/header.html" %}
            <div id="lona"></div>
            {% include "lona/footer.html" %}
            {{ Lona.load_scripts() }}
            <script>
                var lona_context = new Lona.LonaContext({
                    target: '#lona',
                    title: 'Lona',
                    update_address_bar: true,
                    update_title: true,
                    follow_redirects: true,
                    follow_http_redirects: true,
                });

                {% include "lona/frontend.js" %}

                lona_context.setup();
            </script>
        </body>
    </html>



Loading static files
~~~~~~~~~~~~~~~~~~~~

To load static files, that are not part of a widget, Lona defines a filter.

.. code-block:: html

    <link href="{{ Lona.load_static_file('style.css') }}" rel="stylesheet">


Hooks
~~~~~

The Lona context has a number of hooks that are called for different events.


Server disconnect
`````````````````

This hook gets called when the webbsocket connection is lost.

.. code-block:: javascript

      lona_context.add_disconnect_hook(function(lona_context, event) {
        document.querySelector('#lona').innerHTML = 'Server disconnected';
      });


View Start Timeout
``````````````````

When the server is under heavy load it can happen that a view does not start
immediately. This hook is used to give the user feedback that the view gets
started soon, but the client is waiting for the server to respond.

The timeout is triggered when the view needs longer than
``settings.CLIENT_VIEW_START_TIMEOUT`` to start. The default is 2 seconds.

.. code-block:: javascript

      lona_context.add_view_timeout_hook(function(lona_context, lona_window) {
        lona_window.set_html('Waiting for server...');
      });


Input Event Timeout
```````````````````

When the server is under heavy load it can happen that an input event cant be
handled immediately. This hook is used to give the user feedback that the event
gets handled soon, but the client is waiting for the server to respond.

The timeout is triggered when the server needs longer than
``settings.CLIENT_INPUT_EVENT_TIMEOUT`` to handle the input event. The default
is 2 seconds.

.. code-block:: javascript

      lona_context.add_input_event_timeout_hook(function(lona_context, lona_window) {
        alert('Waiting for server...');
      });


Sending Custom Messages
~~~~~~~~~~~~~~~~~~~~~~~

To implement custom features in your frontend like desktop notifications, Lona
supports custom messages. Your messages can contain anything, but may not start
with ``lona:`` because thats the prefix for the Lona protocol.


Client To Server
````````````````

On the server all messages get handled by middlewares.

.. code-block:: javascript

      // templates/lona/frontend.html

    lona_context.send('custom-message:foo');


.. code-block:: python

    # middlewares.py

    class CustomMessagesMiddleware:
        def handle_websocket_message(self, data):
            if not data.message.startswith('custom-message:'):
                return data

            message = data.message.split(':', 1)[1]

            print(message)

**More information:**
`Middlewares </end-user-documentation/middlewares.html>`_


Server To Client
````````````````

The client has a system in place similar to Lona middlewares. You can add a
list of message handlers, that get incoming messages passed in, in the order of
their registration. If a message handler returns the given message, the
message gets passed to the next message handler. If not the message is regarded
as handled.

.. code-block:: python

    # views.py

    from lona import LonaView


    class CustomMessageView(LonaView):
        def handle_request(self, request):
            self.send_str('custom-message:foo')


.. code-block:: javascript

    lona_context.add_message_handler(function(lona_context, raw_message) {
        if(!raw_message.startsWith('custom-message:')) {
            return raw_message;
        };

        alert(raw_message);
    });


Writing A Custom Frontend View
------------------------------

.. code-block:: python

    # views/frontend.py

    from lona import LonaView


    class FrontendView(LonaView):
        def handle_request(self, request):
            return {
                'template': 'path/to/your/template.html',
                'foo': 'bar',
            }

.. code-block:: python

    # settings.py

    FRONTEND_VIEW = 'views/frontend.py::FrontendView'
