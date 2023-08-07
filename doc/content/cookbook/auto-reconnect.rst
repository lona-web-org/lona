

Auto-Reconnect
==============

For development or kiosk applications it can be useful to have a frontend that
reconnects automatically when the server restarts.

This example implements a simple clock that updates the current time once per
second. The script adds a simple snipped to the frontend, which uses the
`server disconnect hook </api-reference/frontends.html#server-disconnect>`_
to try to reconnect the Lona client once per second, when the server restarts.


.. code-block:: python

    from datetime import datetime

    from lona import LonaApp, LonaView
    from lona.html import HTML, H1, P

    app = LonaApp(__file__)


    @app.route('/')
    class MyLonaView(LonaView):
        def handle_request(self, request):
            timestamp = P()

            html = HTML(
                H1('Clock'),
                timestamp,
            )

            while True:
                timestamp.set_text(str(datetime.now()))

                self.show(html)

                self.sleep(1)


    app.add_template('lona/frontend.js', """
        lona_context.add_disconnect_hook(function(lona_context, event) {
            document.querySelector('#lona').innerHTML = `
                Server disconnected <br> Trying to reconnect...
            `;

            setTimeout(function() {
                lona_context.reconnect();

            }, 1000);
        });
    """)


    if __name__ == '__main__':
        app.run(port=8080)
