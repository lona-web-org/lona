

Limit Concurrent Views
======================

.. code-block:: python

    # settings.py

    MAX_USERS = 10
    MAX_VIEWS_PER_USER = 10

    MAX_WORKER_THREADS = MAX_USERS * MAX_VIEWS_PER_USER * 2
    MAX_RUNTIME_THREADS = MAX_USERS * MAX_VIEWS_PER_USER

    MIDDLEWARES = [
        'middlewares/user_limit_middleware.py::UserLimitMiddleware',
    ]

.. code-block:: python

    # middlewares/user_limit_middleware.py

    class UserLimitMiddleware:
        def handle_connection(self, data):
            server = data.server
            connection = data.connection

            if(not server.user_is_connected(connection.user) and
               server.get_connected_user_count() >= server.settings.MAX_USERS):

                return """
                    <h1>To many Users</h1>
                """

            return data

        def handle_request(self, data):
            server = data.server
            request = data.request

            CONCURRENT_VIEWS_PER_USER_MAX = \
                server.settings.CONCURRENT_VIEWS_PER_USER_MAX

            # the frontend has to be visible at all times
            if request.frontend:
                return data

            # reconnecting to a already running view doesn't cost us a thread
            if server.view_is_already_running(request):
                return data

            if(server.get_running_views_count(request.user) <
               server.settings.MAX_VIEWS_PER_USER):

                return data

            return """
                <h1>To many Views<h1>
            """
