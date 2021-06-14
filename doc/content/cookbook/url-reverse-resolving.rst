

URL Reverse Resolving
=====================

.. code-block:: python

    # routes.py

    from lona.routing import Route

    routes = [
        Route('/url-args/<arg1>/<arg2>/', 'views.py::URlArgsView',
              name='url-args-view'),

        Route('/', 'views.py::HomeView', name='home-view'),
    ]


.. code-block:: python

    # views.py

    from lona.view import LonaView


    class URLArgsView(LonaView):
        def handle_request(self, request):
            return '<h1>URLArgsView</h1><p>{}</p>'.format(
                repr(request.match_info),
            )


    class HomeView(LonaView):
        def handle_request(self, request):
            return {
                'redirect': self.server.reverse(
                    'url-args-view',
                    arg1='foo',
                    arg2='bar',
                )
            }