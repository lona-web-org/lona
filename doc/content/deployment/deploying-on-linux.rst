search_index_weight: 10


Deploying on Linux
==================


Deploying A Lona Script
-----------------------

In this section we will deploy a simple
`Lona Script </api-reference/lona-scripts.html>`_ using
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


    if __name__ == '__main__':
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
`Lona Shell Server </api-reference/debugging.html#lona-shell>`_ using
a unix domain socket in ``/srv/lona/lona-project-template/lona_project`` for
debugging and monitoring.

When the project is deployed like defined here, you can attach a
`Lona Shell </api-reference/lona-shell.html>`_ when the server is
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
