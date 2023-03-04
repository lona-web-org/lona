

5. Responses
============

For every incoming request, Lona instantiates an object of the class
``lona.View`` and calls its ``handle_request()`` method to retrieve a
``lona.Response`` object.

In Lona, views can be "interactive" or "non-interactive". Interactive means
that the browser and the view are connected via a WebSocket, so data can flow
both ways, and non-interactive means the browser uses only simple HTTP to
connect to a view.

All views in Lona are interactive by default, to make things like live-updates,
and click events possible. Non-interactive views can be used to implement more
traditional views, like JSON-APIs for example:

.. code-block:: python

    from lona import View, App, JsonResponse

    app = App(__file__)


    # this flag tells Lona to use this view non-interactive
    @app.route('/json-data', interactive=False)
    class JSONResponseView(View):
        def handle_request(self, request):
            return JsonResponse(
                {'foo': 'bar'},
            )


    app.run()

Lona responses can be used for redirects, HTTP-redirects, to return JSON or
binary data.

**More information:**
    - `Request Objects </api-reference/views.html#request-objects>`_
    - `Response Objects </api-reference/views.html#response-objects>`_


.. rst-buttons::

    .. rst-button::
        :link_title: 4. Routing
        :link_target: /tutorial/04-routing/index.rst
        :position: left

    .. rst-button::
        :link_title: 6. HTML
        :link_target: /tutorial/06-daemon-views/index.rst
        :position: right
