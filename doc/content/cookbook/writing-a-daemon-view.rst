

Writing A Daemon View
=====================

By default a view gets killed when its user disconnects. To write views that
can continue in background use ``LonaView.daemonize()``.

When the user comes back and reuses the URL, he gets reconnected with the
running view.

.. code-block:: python

    from datetime import datetime

    from lona.html import HTML, Span, H1, Br, Button
    from lona.view import LonaView


    class DaemonView(LonaView):
        def handle_request(self, request):
            self.timestamp = Span()

            html = HTML(
                H1('Daemon View'),
                'running since: ', Span(str(datetime.now())),
                Br(),
                'last update: ', self.timestamp,
                Br(),
                Button('Stop View', _id='stop-view'),
            )

            self.daemonize()
            self.running = True

            while self.running:
                self.timestamp.set_text(str(datetime.now()))
                self.show(html)
                self.sleep(1)

        def handle_input_event(self, input_event):
            if input_event.node_has_id('stop-view'):
                self.running = False
