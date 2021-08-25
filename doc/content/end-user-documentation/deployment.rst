

Deployment
==========

Resource Management
-------------------

Lona is based on multi-threading (more information:
`Asynchronous Code </basic-concept.html#asynchronous-code>`_).
That means that every hook of a ``lona.LonaView`` like ``handle_request()`` or
``handle_input_event()`` block one thread each until your business logic
finishes.

When planing resources for your application keep in mind that every view that
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
~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~

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


Deploying A Lona Script
-----------------------

In this section we will deploy a simple
`Lona Script </end-user-documentation/lona-scripts.html>`_ using
`systemd <https://systemd.io/>`_ and `Apache2 <https://httpd.apache.org/>`_
as `reverse proxy <https://en.wikipedia.org/wiki/Reverse_proxy>`_


Lona
~~~~

.. code-block:: bash

    # installing the necessary debian/ubuntu packages
    $ sudo apt install apache2 python3 python3-venv

    # setup /srv/lona and python virtualenv
    $ sudo mkdir -p /srv/lona
    $ sudo python3 -m venv /srv/lona/env
    $ source /srv/lona/env/bin/activate
    $ (env) pip install lona

    # setup lona script
    $ sudo touch /srv/lona/my-script.py

    # change ownership of /srv/lona to www-data
    $ sudo chown -R www-data:www-data /srv/lona


.. code-block:: python

    # /srv/lona/my-script.py

    from lona.html import HTML, Button, Div, H1
    from lona import LonaApp, LonaView

    app = LonaApp(__file__)

    app.settings.MAX_RUNTIME_THREADS = 50
    app.settings.MAX_WORKER_THREADS = 100
    app.settings.MAX_STATIC_THREADS = 20


    @app.route('/')
    class MyView(LonaView):
        def handle_request(self, request):
            message = Div('Button not clicked')
            button = Button('Click me!')

            html = HTML(
                H1('Click the button!'),
                message,
                button,
            )

            self.show(html)

            # this call blocks until the button was clicked
            input_event = self.await_click(button)

            if input_event.node == button:
                message.set_text('Button clicked')

            return html


    app.run(port=8080)


Apache2
~~~~~~~

.. code-block:: shell

    $ sudo a2enmod headers rewrite proxy proxy_wstunnel proxy_http proxy_balancer lbmethod_byrequests

.. code-block:: xml
    :include: configs/lona-script-apache.conf

.. code-block:: shell

    $ sudo a2ensite lona.conf


Systemd
~~~~~~~

.. code-block:: ini
    :include: configs/lona-script.service

.. code-block:: text

    $ sudo systemctl enable lona-server.service
    $ sudo systemctl start lona-server.service


Deploying A Lona Project
------------------------

In this section we will deploy
`lona-project-template <https://github.com/lona-web-org/lona-project-template>`_
using `Apache2 <https://httpd.apache.org/>`_ and
`systemd <https://systemd.io/>`_.

Lona collects all static file at startup once and places them in
``/srv/lona/static`` to make them available for Apache.

The Lona server service sets up a
`Lona Shell Server </end-user-documentation/debugging.html#lona-shell>`_ using
a unix domain socket in ``/srv/lona/lona-project-template/lona_project`` for
debugging and monitoring.

When the project is deployed like defined here, you can attach a
`Lona Shell </end-user-documentation/lona-shell.html>`_ when the server is
running.

.. code-block:: txt

    $ sudo /srv/lona/lona-project-template/env/bin/rlpython file:///srv/lona/lona-project-template/lona_project/socket

Lona
~~~~

.. code-block:: bash

    # installing the necessary debian/ubuntu packages
    $ sudo apt install apache2 build-essential python3 python3-venv

    # setup /srv/lona and python virtualenv
    $ sudo mkdir -p /srv/lona
    $ sudo mkdir -p /srv/lona/static
    $ sudo git clone https://github.com/lona-web-org/lona-project-template /srv/lona/lona-project-template
    $ cd /srv/lona/lona-project-template
    $ sudo make env

    # change ownership of /srv/lona to www-data
    $ sudo chown -R www-data:www-data /srv/lona



Apache2
~~~~~~~

.. code-block:: shell

    $ sudo a2enmod headers rewrite proxy proxy_wstunnel proxy_http proxy_balancer lbmethod_byrequests

.. code-block:: xml
    :include: configs/lona-project-apache.conf

.. code-block:: shell

    $ sudo a2ensite lona.conf


Systemd
~~~~~~~

.. code-block:: ini
    :include: configs/lona-project.service

.. code-block:: text

    $ sudo systemctl enable lona-server.service
    $ sudo systemctl start lona-server.service
