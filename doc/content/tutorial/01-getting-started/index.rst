

01 Getting Started
==================

Lona apps can be structured as
`projects <https://github.com/lona-web-org/lona-project-template>`_ and as
{{ link('/api-reference/lona-scripts.rst', 'scripts') }}. Both structures have
the same features, and can easily be migrated from one to another.

In this tutorial we will focus on scripts, because they are easier to setup,
and the examples are easier to copy-paste.

Lona is a web application server and rendering framework, so it comes with a
very bland (or lack of) styling. We will use
`lona-picocss <https://github.com/lona-web-org/lona-picocss#readme>`_  in this
tutorial, so our app will look nice from the start.


Prerequisites
-------------

Lona requires at least Python 3.7, and is built on top of aiohttp and Jinja2,
so you need to be able to run pip on your system.
The web application server should be compatible with any system that can run
Python, but some debug features, like the debug shell, might have some
problems on non-unix systems.


Installation
------------

If you want to use Lona locally in a project directory, and don't want to
install Lona globally, use a
`virtualenv <https://docs.python.org/3/library/venv.html>`_ (this step can be
skipped).

.. code-block::

    python3 -m venv env
    source env/bin/activate

These two commands set you up with a virtualenv, and then "source" it, so
the virtualenv will be used in the current shell. You will have to repeat the
second step when you close and reopen your shell.

Lona is packaged, and distributed on `pypi <https://pypi.org/>`_. Use
`pip <https://pip.pypa.io/en/stable>`_ to install Lona.

.. code-block::

    pip install lona lona-picocss


Run Lona
--------

Put this example into a new Python file.

.. code-block:: python
    :include: example-1.py

The script creates an app, using the ``lona.App`` class, using ``__file__`` as
the **project root**.

Every Lona script and project has a **project root**. Every path, within the
app, like template paths, static directories or routes, will be relative to
this directory.

The last line of the script (``app.run()``), will run the application server,
and block until ``CTRL-C`` was hit.

Run the script using:

.. code-block::

    python example.py

``app.run()`` takes keywords like ``host`` or ``port`` for configuration, and
also parses the command line. Run ``python example.py -h`` to print the help.

The script should print that it opened a webserver on
``http://localhost:8080``. If you navigate your browser there, you should see
this:

.. image:: it-works.gif


Hello World
-----------

The previous example had no actual view in it. Extend your script like this
to create a simple hello world.

.. code-block:: python
    :include: example-2.py

Restart your script using ``CTRL-C`` and navigate to ``http://localhost:8080``.
This second example will be our template for the rest of the tutorial.

.. image:: hello-world.gif


The Server Reference
--------------------

In Lona, the {{ link('/api-reference/server.rst', 'server') }} reference is the
central place where all settings and runtime state lives. It is available in
every view using ``self.server``, in every middleware and in the shell.


Settings
--------

Lona is highly configurable and most of its inner workings can be configured
using settings. In Lona projects, settings are set in one or more dedicated
``settings.py`` files. In scripts, settings can be set via the
``app.settings`` property.

A full list of all default settings can be found here:
{{ link('/api-reference/settings.rst', 'Settings') }}.

It is highly encouraged to define custom settings for your specific use-case,
or for Lona extensions, as long as their names do not clash with the default
settings.

.. code-block:: python
    :include: example-3.py


Import Strings
--------------

Lona implements a special form of import strings, to make loading of
application code, as easy as possible. Lona can load views, routes middlewares
etc from modules, third-party-packages and even simple Python scripts that
would not be importable by Python otherwise.

.. code-block:: python

    # load from a module
    Route('/', 'my_app.views.IndexView'),

    # load from a third-party-package
    Route('/settings', 'lona_picocss.views.SettingsView'),

    # load from a script
    Route('/my-view', './views.py::MyView'),


Debugging
---------

For debugging, Lona comes with a builtin shell, powered by
`rlpython <https://github.com/fscherf/rlpython>`_. rlpython is an REPL, so it
accepts valid Python expressions, and also custom commands using the prefix
``%``.

Lona defines a list of useful commands, for example to get a list of all
currently running views, or to print all settings, environment variables and
state. All Lona specific commands are prefixed ``%lona_`` and have a builtin
help, that can be printed using ``-h``.

The shell can be run from the same shell that the application server uses,
using ``python example.py --shell``. Hit ``CTRL-D`` to exit the shell, and stop
the server.

**More Information:** {{ link('/api-reference/lona-shell.rst', 'Lona Shell') }}

.. image:: lona-shell.gif

.. rst-buttons::

    .. rst-button::
        :link_title: 02 HTML
        :link_target: /tutorial/02-html/index.rst
        :position: right
