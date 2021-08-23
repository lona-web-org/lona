

Sessions
========

Lona has built-in, HTTP cookie based session system that provides user sessions
without login. This makes personal daemonized views possible.

**Settings:**
`Session Settings </end-user-documentation/settings.html#sessions>`_

.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            print(request.user)  # prints "<AnonymousUser(CUiUvxtCHxEMMobEqqqDeqtsjMyu)>"


Workflow
--------

If ``settings.SESSIONS`` is enabled, the middleware
``lona.middleware.sessions.SessionMiddleware`` checks if a cookie with the name
specified in ``settings.SESSIONS_KEY_NAME`` is set. If not, the middleware
generates a random key using ``settings.SESSIONS_KEY_GENERATOR``, sets the
cookie and triggers a HTTP reload to make the browser return with the new set
cookie.

When the session key is present, the middleware sets up a
``lona.middleware.sessions.AnonymousUser`` with the session key set in
``request.user``.

.. note::

    The cookie setting and redirecting workflow is skipped on non-interactive
    views to make REST APIs work as expected