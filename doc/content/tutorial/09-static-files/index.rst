

09 Static Files
===============

Lona has a dynamic loading mechanism for static files like CSS or JavaScript.

Any node and view can define a list of static files in ``Node.STATIC_FILES`` or
``VIEW.STATIC_FILES`` to tell the frontend which files are required, in order
to render the node or view correctly. This makes packaging of components
possible.

This example shows a custom node that ships with a CSS file to color its
content red.

.. image:: example-1.gif

.. code-block:: python
    :include: example-1.py

.. code-block:: css
    :include: red-colored-div.css

**More information:** `Static Files </api-reference/html.html#adding-javascript-and-css-to-html-nodes>`_

.. rst-buttons::

    .. rst-button::
        :link_title: 08 Middlewares
        :link_target: /tutorial/08-middlewares/index.rst
        :position: left

    .. rst-button::
        :link_title: 10 Widgets
        :link_target: /tutorial/10-widgets/index.rst
        :position: right
