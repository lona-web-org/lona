

Integrating Django
==================

.. code-block:: txt

    # REQUIREMENTS.txt

    aiohttp_wsgi

.. code-block:: python

    # routes.py

    from lona.routing import Route, MATCH_ALL
    from aiohttp_wsgi import WSGIHandler

    from your_project.wsgi import application

    wsgi_handler = WSGIHandler(application)


    routes = [
        Route(MATCH_ALL, wsgi_handler, http_pass_through=True),
    ]