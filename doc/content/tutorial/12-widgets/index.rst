

12. Widgets
===========

Lona is all about managing state and business logic on the backend, using a
stateless frontend. This approach creates a certain delay because for every
reaction to an event, a round-trip to the server is necessary. This is not a
problem for simple tasks, like handling a simple button press, but becomes an
issue when dealing with time-critical operations like animations.

To perform operations on the client, Lona nodes can define widgets, which are
JavaScript classes that get initialized when the node get rendered in the
browser. This widget has a reference to the node and its state and has full
control over it.

The server-side node can share state with the browser-side widget, by setting
``Node.widget_data``. This property behaves like a Python dictionary, and is
thread-safe, using the `lock </tutorial/02-html/index.html#locking>`_ of its
node.

.. note::

    Widget data can only be changed on the server. Changes to ``Widget.data``
    on the browser-side are not supported.

    To issue a change from the browser-side, fire a
    `custom event <api-reference/html.html#firing-custom-input-events>`_,
    and apply your change on the server.

This example shows a widget that renders a rotation animation on the
browser-side. The server-side does not render the animation itself, but
controls its parameters using ``Widget.data``.

.. image:: example-1.gif

.. code-block:: python
    :include: example-1.py

.. code-block:: javascript
    :include: rotating-container.js


.. rst-buttons::

    .. rst-button::
        :link_title: 11. Static Files
        :link_target: /tutorial/11-static-files/index.rst
        :position: left

    .. rst-button::
        :link_title: 13. Frontends
        :link_target: /tutorial/13-frontends/index.rst
        :position: right
