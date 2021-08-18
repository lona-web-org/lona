

Debugging
=========

Lona Server Command Line Options
--------------------------------

.. note::

    When using a GNU make based project like in the
    `Getting Started </end-user-documentation/getting-started.html>`_ you
    can use ``args=""`` to set command line options

    ``make server args="--host=0.0.0.0 --port=80 --shell"``

.. table::

    ^Option           ^Description
    |-l / --log-level |Set log level to [debug,info,warn,error,critical]
    |--loggers        |Enable or disable a given list of loggers <br> To include a logger use "+{LOGGER_NAME}", to exclude "_{LOGGER_NAME}"
    |--debug-mode     |Enable debug log for {messages,views,input-events}
    |--shell          |Embed a shell in the same process as the server
    |--shell-server   |Starts rlpython shell server containing a Lona shell <br> More Information: <a href="#lona-shell">Lona Shell</a>
    |-o               |Set setting to value before settings.py got loaded <br> example "-o MY_FEATURE=True"
    |-O               |Set setting to value after settings.py got loaded <br> example "-o MY_FEATURE=True"


Lona Client
-----------

CLIENT_RECOMPILE
~~~~~~~~~~~~~~~~

By default the Lona client and all its discovered modules get compiled once at
startup. To recompile on every request you can set
``settings.CLIENT_RECOMPILE`` to ``True`` or use ``-O CLIENT_RECOMPILE=True``
from the command line.


TEST_VIEW_START_TIMEOUT
~~~~~~~~~~~~~~~~~~~~~~~

To test `View Start Timeouts </end-user-documentation/frontends.html#view-start-timeout>`_
you can set ``settings.TEST_VIEW_START_TIMEOUT`` to ``True`` or use
``-O TEST_VIEW_START_TIMEOUT=True`` from the command line.

When this setting is set, Lona will introduce an arbitrary delay of
``settings.CLIENT_VIEW_START_TIMEOUT`` plus 1 Second before a view gets
started.


TEST_INPUT_EVENT_TIMEOUT
~~~~~~~~~~~~~~~~~~~~~~~~

To test `View Input Event Timeouts </end-user-documentation/frontends.html#input-event-timeout>`_
you can set ``settings.TEST_INPUT_EVENT_TIMEOUT`` to ``True`` or use
``-O TEST_INPUT_EVENT_TIMEOUT=True`` from the command line.

When this setting is set, Lona will introduce an arbitrary delay of
``settings.CLIENT_INPUT_EVENT_TIMEOUT`` plus 1 Second before an input event
gets handled.


Lona Shell
----------

The Lona shell is based on `rlpython <https://pypi.org/project/rlpython/>`_ and
can be started directly from the server process using ``--shell``, when using
script using ``app.run(shell=True)`` and a shell server and can be embedded
using ``server.embed_shell()`` or ``LonaView.embed_shell()``.

The shell is a full python REPL and contains some use full commands prefixed
with ``%lona_``.

.. table::

    ^Command                                        ^Description
    |%threads [THREAD_ID]                           |Prints all threads or all information on given thread
    |%lona_info                                     |Prints basic information about the running Lona server <br> and its configuration
    |%lona_settings [SETTINGS_NAME]                 |Prints one or all settings
    |%lona_routes [-r URL]                          |Prints all or the matching routes when URL is provided
    |%lona_connections                              |Prints all current server connections
    |%lona_server_state                             |Prints server.state
    |%lona_views [RUNTIME_ID] [--memory]            |Prints all running views or all information on given <br> view. When "--memory" is set, all current variables <br> of the view get printed
    |%lona_static_files [-l] [-r NAME] [static-dir] |Prints all loaded static files or static file directories
    |%lona_templates [-l] [-r NAME] [template-dir]  |Prints all loaded templates or template directories
    |%lona_middlewares                              |Prints all loaded middleware hooks


Using Lona Shell Server
~~~~~~~~~~~~~~~~~~~~~~~

Lona supports rlpython's remote shell feature. With ``--shell-server`` set
Lona server binds to a port or a unix domain socket.

.. code-block:: txt

    $ lona run-server --shell-server=file://socket
    $ lona run-server --shell-server=localhost:8080

To attach run

.. code-block:: txt

    $ rlpython file://socket
    $ rlpython localhost:8080

or if you use the project template from
{{ link('end-user-documentation/getting-started.rst', 'Getting Started') }}
you can run

.. code-block:: txt

    $ make server-shell