

8. State
========

Global State
------------

Lona defines a global state object in ``server.state``, that is thread-safe and
can be used to share application specific data between views, middlewares and
all other parts of a Lona app that have access to the ``server`` reference.

``server.state`` behaves like a Python dictionary, and implements the same
locking interface as `HTML nodes </tutorial/02-html/index.html#locking>`_.

.. code-block:: python

    from datetime import datetime

    from lona.html import HTML, H1, P
    from lona import View, App

    app = App(__file__)

    # set initial state
    app.settings.INITIAL_STATE = {
        'start_time': datetime.now(),
    }


    @app.route('/')
    class StateViewView(View):
        def handle_request(self, request):

            # get start_time from global state
            start_time = this.server.state['start_time']

            return HTML(
                H1('Start Time'),
                P(f'This application runs since {start_time}')
            )


    app.run()


Node State
----------

Every Lona node has its own state object that is only available on the server,
and gets not synchronized with the browser. This can be used to attach
sensitive data to a node, like a database id, to retrieve it later.

``Node.state`` has the same API as the global state object, but its lock is
shared with the nodes lock. That means you can change the server-side and the
browser-side data in one transaction.


.. code-block:: python

    from datetime import datetime

    from lona.html import HTML, H1, P, Button
    from lona import View, App

    app = App(__file__)

    # this is sensitive data
    database = {
        312: 'Bob':
        320: 'Alice'
        222: 'Carl',
    }


    @app.route('/')
    class StateViewView(View):
        def delete_from_database(self, input_event):

            # retrieve state from the clicked button
            database_id = input_event.node.state['id']

            # remove key from the database
            database.remove(database_id)

        def handle_request(self, request):
            html = HTML(
                H1('Delete Database Rows'),
            )

            for key, value in database.items():
                button = Button(
                    f'Delete {value}',
                    handle_click=delete_from_database,

                    # set state that should not be visible in the browser
                    state={
                        'id': key,
                    },
                )

                html.append(button)

            return html


    app.run()


.. rst-buttons::

    .. rst-button::
        :link_title: 7. Daemon Views
        :link_target: /tutorial/07-daemon-views/index.rst
        :position: left

    .. rst-button::
        :link_title: 9. Middlewares
        :link_target: /tutorial/09-middlewares/index.rst
        :position: right
