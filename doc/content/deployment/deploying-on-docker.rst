search_index_weight: 10


Deploying on Docker
===================

In this article we will deploy a simple Lona script using
`Docker <https://www.docker.com/>`_ and optionally
`Docker Compose <https://docs.docker.com/compose/>`_.

See the `lona-project-template <https://github.com/lona-web-org/lona-project-template>`_
for an example on how to run a Lona Project in Docker.

This article assumes that all files (``hello-world.py``, ``Dockerfile`` and
optionally ``docker-compose.yml``) are in the same directory, and all commands
are run in this directory.

.. code-block:: python
   :include: hello-world.py

.. code-block:: docker
   :include: Dockerfile

Run these two commands:

.. code-block:: bash

    docker build -t lona-hello-world .
    docker run -it -p 8080:8080 lona-hello-world


Docker Compose
--------------

To use `Docker Compose <https://docs.docker.com/compose/>`_, add this this
config to the same directory.

.. code-block:: yaml
   :include: docker-compose.yml

Then run this command:

.. code-block:: bash

    docker compose up  # on your system it might be 'docker-compose'
