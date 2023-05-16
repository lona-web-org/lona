is_template: False


13. Frontends
=============

Lona is a single-page application framework. That means that the page gets
loaded once, and when a link or button is clicked, only the content of the
main container gets updated (this container is called the "Lona window"
internally). Until now, all examples contained only code within
this main container, but not the page around it. In Lona, these pages are
called "frontend".

A Lona frontend is a combination of a specialized Lona view that runs when a
connection is made to the server, and a Jinja2 template that serves and sets up
the Lona JavaScript client. For most applications the default Frontend view of
Lona will suffice, and only the Jinja2 template needs to be changed.

Packages like `lona-picocss <https://github.com/lona-web-org/lona-picocss/blob/master/lona_picocss/templates/picocss/base.html>`_
ship their own template.

.. code-block:: html

    <!-- templates/lona/frontend.html -->

    <!doctype html>
    <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">

            <!-- load all required CSS stylesheets -->
            {{ Lona.load_stylesheets() }}
        </head>
        <body>

            <!-- navigation -->
            <nav id="navigation">
                <ul>
                    <li><a href="/">Home</a></li>
                    <li><a href="/page-1/">Page 1</a></li>
                    <li><a href="/page-2/">Page 2</a></li>
                </ul>
            </nav>

            <!-- all views will be rendered in here -->
            <main id="lona"></main>

            <!-- load all required JavaScript files -->
            {{ Lona.load_scripts() }}

            <!-- setup Lona JavaScript client -->
            <script>
                window.addEventListener('load', () => {
                    const lona_context = new Lona.LonaContext({
                        target: 'main#lona',
                        title: 'Lona',
                        update_address_bar: true,
                        update_title: true,
                        follow_redirects: true,
                        follow_http_redirects: true,
                    });

                    // gets called when the websocket connection
                    // to the server was made
                    lona_context.add_connect_hook((lona_context) => {

                        // patch navigation links so the page does not
                        // reload but uses the websocket connection to start
                        // new views
                        lona_context.patch_input_events('nav#navigation');
                    });

                    // gets called when the server disconnects
                    lona_context.add_disconnect_hook((lona_context) => {
                        document.querySelector('main#lona').innerHTML = `
                            <h1>Server Disconnected</h1>
                            <p>Trying to reconnect</p>
                        `;

                        // try to reconnect once a second
                        setTimeout(() => {
                            lona_context.reconnect();

                        }, 1000);
                    });

                    // gets called when a view takes a long time to start
                    lona_context.add_view_timeout_hook((lona_context, lona_window) => {
                        lona_window.set_html(`
                            <h1>Waiting For Server</h1>
                        `);
                    });

                    // gets called when the server takes a long time to respond
                    // to input events
                    lona_context.add_input_event_timeout_hook((lona_context, lona_window) => {
                        alert('Waiting for server');
                    });

                    // setup
                    lona_context.setup();
                    window['lona_context'] = lona_context;
                });
            </script>
        </body>
    </html>

**More information:** `Frontends </api-reference/frontends.html>`_


.. rst-buttons::

    .. rst-button::
        :link_title: 12. Widgets
        :link_target: /tutorial/12-widgets/index.rst
        :position: left
