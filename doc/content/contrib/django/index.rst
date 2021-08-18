toctree: False


lona-django
===========

Support for Django authentication, authorization and sessions are implemented
in `https://github.com/lona-web-org/lona-django <https://github.com/lona-web-org/lona-django>`_.

More information on how to integrate Django in your Lona project:
{{ link('cookbook/integrating-django.rst', 'Integrating Django') }}


Installation
------------

.. code-block:: text

    $ pip install lona-django


Django Auth
-----------

Django authentication, authorization and sessions are implemented in a Lona
middleware.

.. code-block:: python

    # settings.py

    MIDDLEWARES = [
        'lona_django.middlewares.DjangoSessionMiddleware',
    ]

To configure authorization use the view flags listed below. The flags are
all optional and can be mixed.

The Django user associated with the given request is available in
``request.user``.

.. code-block:: python

    # views.py

    from lona import LonaView

    class DjangoView(LonaView):
        DJANGO_AUTH_LOGIN_REQUIRED = False
        DJANGO_AUTH_STAFF_REQUIRED = False
        DJANGO_AUTH_STAFF_PERMISSION_OVERRIDE = True
        DJANGO_AUTH_PERMISSIONS_REQUIRED = []
        DJANGO_AUTH_GROUPS_REQUIRED = []

        def handle_request(self, request):
            user = request.user
