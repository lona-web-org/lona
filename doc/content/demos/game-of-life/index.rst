

Game Of Life
============

.. img:: game-of-life.gif

.. warning::

    Lona renders on top of the browsers DOM API. Therefore every "pixel" in
    this demo is a ``div``, which is very inefficient.

    Lona is not meant to be used as a game engine. This is just a tech-demo
    that Lona can handle large node trees and complex user-interaction.


Install dependencies
--------------------

.. code-block:: text

    pip install lona numpy


Source Code
-----------

.. code-block:: python
    :include: game-of-life.py
