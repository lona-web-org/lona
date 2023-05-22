

Daemonized View
===============

.. img:: daemonized-view.gif

By default a view gets killed when its user disconnects (this happens when
the tab gets refreshed or another URL gets requested).

When ``LonaView.daemonize()`` is called, Lona lets views continue running in
background when the user disconnects. The user can also attach multiple tabs
to the same view then.

.. note::

    Daemonized views are not meant to be used to create multi-user views. They
    are meant to create single-user views that are long running (multiple
    minutes or hours).

    For example if you write a view that process a huge amount of data, and
    you want to push a progress bar forward.


Install Dependencies
--------------------

.. code-block:: text

    pip install lona lona-chartjs


Source code
-----------

.. code-block:: python
    :include: daemonized-view.py
