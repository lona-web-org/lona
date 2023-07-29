search_index_weight: 10


Resource Management
===================

Lona is based on multi-threading (more information:
`Asynchronous Code </basic-concept.html#asynchronous-code>`_).
That means that every hook of a ``lona.LonaView`` like ``handle_request()`` or
``handle_input_event()`` block one thread each until your business logic
finishes.

When planning resources for your application keep in mind that every view that
runs can use up to three threads at a time (one for ``handle_request()``, one
for ``handle_input_event()`` and one for messaging between server and client).

Lona splits threading up in two pools: the ``view_runtime_pool`` and the
``worker_pool``, configured through ``settings.MAX_RUNTIME_THREADS`` and
``settings.MAX_WORKER_THREADS``.

``LonaView.handle_request()``, the main entry point for view business logic,
runs in ``view_runtime_pool`` separated from all other Lona tasks because
these are expected to run for a very long time potentially (up to days or
weeks).

All other hooks and messaging runs in ``worker_pool``. Business logic that
runs there is expected to don't run that long, but with a much higher rate.


Example settings
----------------

These are example settings for an application that servers 50 concurrent users
with one running view for each user. 50 views can run at a time. Because a view
can use up to two worker threads the ``worker_pool`` should be at least twice
as big as ``view_runtime_pool``.

When running as a Lona script, static files like CSS, Javascript etc. get
served by Lona itself. ``settings.MAX_STATIC_THREADS`` configures how many
threads handle static file serving.


.. code-block:: python

    MAX_RUNTIME_THREADS = 50
    MAX_WORKER_THREADS = 100
    MAX_STATIC_THREADS = 20


Using Multiple Processes
------------------------

Because of the
`Python Gil <https://wiki.python.org/moin/GlobalInterpreterLock>`_ only one
python thread can run at a time. Depending on your application and hardware it
can make sense to start the same Lona project or script on multiple ports and
use a
`load balancer <https://en.wikipedia.org/wiki/Load_balancing_(computing)>`_
like `Apache2 <https://httpd.apache.org/>`_ to distribute the load to multiple
Python processes.

All Apache configs in this article use Apaches load balancing feature to
implement reverse proxying. To expand the balancing pool just add more than
one member on port ``8080``.
