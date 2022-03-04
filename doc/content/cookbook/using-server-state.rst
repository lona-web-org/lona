

Using Server State
==================

To communicate between multiple views and middlewares, Lona has a atomic state
object in ``server.state`` that behaves like a ``Dict``. All access to
``server.state`` triggers ``server.state.lock`` implicit. To perform multiple
accesses in a transaction, ``server.state.lock`` can be used explicit.


.. code-block:: python

    from lona import LonaView


    class MyLonaView(LonaView):
        def handle_request(self, request):
            with self.server.state.lock:
                self.server.state['foo'] = 'foo'
                self.server.state['bar'] = 'bar'

            print(self.server.state['foo'])

The ``server.state`` can be initialized in the settings using ``INITIAL_SERVER_STATE``:

.. code-block:: python

    # settings.py
    INITITAL_SERVER_STATE = {
        "myvalue": 42,
    }
