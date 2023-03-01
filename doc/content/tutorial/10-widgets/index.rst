

10 Widgets
==========

Lona is all about managing state and business logic on the backend, using a
stateless frontend. This approach has a certain delay to it, because for every
reaction to an event, a round-trip to the server is necessary. This is no
problem for simple tasks, like handling a simple button press, but becomes a
problem when dealing with time-critical operations, like animations.

Lona nodes can define a widget, which is a JavaScript class that gets
initialized when the node gets rendered in the browser. This widget gets a
reference to the node and its state, and has full control over it.

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
controls its parameters, using ``Widget.data``.

.. image:: example-1.gif

.. code-block:: python
    :include: example-1.py

.. code-block:: javascript
    :include: rotating-container.js


.. rst-buttons::

    .. rst-button::
        :link_title: 09 Static Files
        :link_target: /tutorial/09-static-files/index.rst
        :position: left

    .. rst-button::
        :link_title: 11 Frontends
        :link_target: /tutorial/11-frontends/index.rst
        :position: right
