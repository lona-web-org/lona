

Error Views
===========

When an exception is raised in view, an URL is not available or a view
raised a Forbidden error, a Lona error view is called. Lona error views behave
like normal Lona views and use the same API.

Lona has error views for 403, 404 and 500 errors build in that use overrideable
templates.  To customize your Lona application you can override the templates
or the entire views.


Custom Templates
----------------

Lona uses ``settings.`ERROR_403_TEMPLATE`` which is set to
``lona/403.html`` by default. You can reset this value or provide a
template under this path.

403 templates get the ``lona.errors.ForbiddenError`` passed in their template
context.

403 Errors
~~~~~~~~~~

.. code-block:: html

    <!--  templates/lona/403.html -->

    <h1>403</h1>
    <p>Forbidden</p>


404 Errors
~~~~~~~~~~

Lona uses ``settings.`ERROR_404_TEMPLATE`` which is set to
``lona/404.html`` by default. You can reset this value or provide a
template under this path.

.. code-block:: html

    <!--  templates/lona/404.html -->

    <h1>404</h1>
    <p>Not Found</p>


500 Errors
~~~~~~~~~~

Lona uses ``settings.`ERROR_500_TEMPLATE`` which is set to
``lona/500.html`` by default. You can reset this value or provide a
template under this path.

500 templates get the python exception passed in their template
context.

.. code-block:: html

    <!--  templates/lona/500.html -->

    <h1>500</h1>
    <p>Internal Error</p>


Custom Views
------------

403 Errors
~~~~~~~~~~

.. code-block:: python

    # views/error_403.py

    from lona import LonaView


    class Error403View(LonaView):
        def handle_request(self, request, exception):
            return {
                'template': 'lona/403.html',
                'request': request,
            }


.. code-block:: python

    # settings.py

    ERROR_403_VIEW = 'views/error_403.py::Error403View'


404 Errors
~~~~~~~~~~

.. code-block:: python

    # views/error_403.py

    from lona import LonaView


    class Error404View(LonaView):
        def handle_request(self, request):
            return {
                'template': 'lona/404.html',
                'request': request,
            }


.. code-block:: python

    # settings.py

    ERROR_404_VIEW = 'views/error_404.py::Error403View'


500 Errors
~~~~~~~~~~

.. code-block:: python

    # views/error_500.py

    from lona import LonaView


    class Error500View(LonaView):
        def handle_request(self, request, exception):
            return {
                'template': 'lona/500.html',
                'request': request,
                'exception': exception,
            }


.. code-block:: python

    # settings.py

    ERROR_404_VIEW = 'views/error_500.py::Error403View'
