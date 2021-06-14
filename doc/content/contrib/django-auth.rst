

Django Auth
===========

Installation
------------

.. code-block:: python

    # settings.py

    MIDDLEWARES = [
        'lona.contrib.django.auth.DjangoSessionMiddleware',
    ]


Views
-----

.. code-block:: python

    # views.py

    from lona.view import LonaView

    class DjangoView(LonaView):
        DJANGO_AUTH_LOGIN_REQUIRED = False
        DJANGO_AUTH_STAFF_REQUIRED = False
        DJANGO_AUTH_STAFF_PERMISSION_OVERRIDE = True
        DJANGO_AUTH_PERMISSIONS_REQUIRED = []
        DJANGO_AUTH_GROUPS_REQUIRED = []


Settings
--------

.. raw-setting::

    DJANGO_AUTH_USE_LONA_ANONYMOUS_USER = False