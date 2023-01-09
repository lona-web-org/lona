

04 Routing
==========

When a request is made to a Lona app, the routing table is used to determine
which view should be run. The routing table is a list of ``lona.Route``
objects, that gets iterated over until the first route matches (therefore the
order may be important in some cases).

All examples in this tutorial use the ``app.route`` decorator, which appends
a new route, with the decorated view in it, to the routing table. Therefore
the views and routes in a Lona script get tried top to bottom when a request
comes in.

Routes use named regexes that are generated at setup time. By default, URL
args match every character between two slashes, because most URL schemas use
slashes as divider. ``/user/<username>/<nickname>`` will match URLs like
``/user/alice/@alice_1``. To define a custom pattern add a colon to a URL arg
like this: ``/user/<username:[a-z]{3}>/<nickname>``.

To create a route that matches any given route, ``lona.MATCH_ALL`` can be used
instead of an URL.

This example shows a simple greeting view, that uses an URL arg as name.

.. image:: example-1.gif

.. code-block:: python
    :include: example-1.py


Reverse Matching
----------------

In the previous example, the index view used the URL as string to redirect
to the greeting view. That means that both the index view, and the greeting
view have to be changed when the URL changes.

When a route has a name, which can be any string, a complete URL can be reverse
matched using ``Server.reverse()``

.. code-block:: python
    :include: example-2.py

**More information:**
    - `URL Args </api-reference/views.html#url-args>`_
    - `Server.reverse() </api-reference/server.html#server-reverse>`_


.. rst-buttons::

    .. rst-button::
        :link_title: 03 Events
        :link_target: /tutorial/03-events/index.rst
        :position: left

    .. rst-button::
        :link_title: 05 Responses
        :link_target: /tutorial/05-responses/index.rst
        :position: right
