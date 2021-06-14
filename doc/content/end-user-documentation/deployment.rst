

Deployment
==========

In this section we will deploy
`lona-project-template <https://github.com/fscherf/lona-project-template>`_
using `Apache2 <https://httpd.apache.org/>`_ and
`systemd <https://systemd.io/>`_.

The service is split into two systemd services. One for Lona server, the other
one for Lona static files. Lona collects all static file at startup once
and places them in ``/srv/lona/static`` to make them available for Apache.

The Lona server service sets up a
`Lona Shell Server <end-user-documentation/debugging.html#lona-shell>`_ using
a unix domain socket in ``/srv/lona/lona-project-template/lona_project`` for
debugging and monitoring.

To connect to the shell server run

.. code-block:: txt

    $ sudo /srv/lona/lona-project-template/env/bin/rlpython file:///srv/lona/lona-project-template/lona_project/socket


Lona
----

.. code-block:: text

    $ sudo mkdir -p /srv/lona
    $ sudo mkdir -p /srv/lona/static
    $ sudo git clone https://github.com/fscherf/lona-project-template /srv/lona/lona-project-template
    $ sudo chown -R www-data:www-data /srv/lona
    $ cd /srv/lona/lona-project-template
    $ sudo -u www-data make env


Apache2
-------

.. code-block:: shell

    $ sudo apt install apache2
    $ sudo a2enmod headers rewrite proxy proxy_wstunnel proxy_http proxy_balancer lbmethod_byrequests

.. code-block:: xml
    :include: configs/lona.conf

.. code-block:: shell

    $ sudo a2ensite lona.conf


Systemd
-------

.. code-block:: ini
    :include: configs/lona-server.service

.. code-block:: ini
    :include: configs/lona-static.service

.. code-block:: ini
    :include: configs/lona.target

.. code-block:: text

    $ sudo systemctl enable lona-server.service
    $ sudo systemctl enable lona-static.service
    $ sudo systemctl enable lona.target
