search_index_weight: 10


Settings
========

Settings can be live analyzed by using the
{{ link('end-user-documentation/lona-shell.rst', 'Lona Shell') }} command
``%lona_settings``.

Threads
-------

.. setting::
    :name: MAX_WORKER_THREADS
    :path: lona.default_settings.MAX_WORKER_THREADS

.. setting::
    :name: MAX_STATIC_THREADS
    :path: lona.default_settings.MAX_STATIC_THREADS

.. setting::
    :name: MAX_RUNTIME_THREADS
    :path: lona.default_settings.MAX_RUNTIME_THREADS


Routing
-------

.. setting::
    :name: ROUTING_TABLE
    :path: lona.default_settings.ROUTING_TABLE

.. setting::
    :name: ROUTING_RESOLVE_CACHE_MAX_SIZE
    :path: lona.default_settings.ROUTING_RESOLVE_CACHE_MAX_SIZE

    Lona uses a ``functools.lru_cache`` to cache resolving requests. This
    setting configures the max size of this cache.

.. setting::
    :name: ROUTING_REVERSE_CACHE_MAX_SIZE
    :path: lona.default_settings.ROUTING_REVERSE_CACHE_MAX_SIZE

    Lona uses a ``functools.lru_cache`` to cache reverse resolving requests.
    This setting configures the max size of this cache.


Templating
----------

.. setting::
    :name: TEMPLATE_DIRS
    :path: lona.default_settings.TEMPLATE_DIRS

.. setting::
    :name: FRONTEND_TEMPLATE
    :path: lona.default_settings.FRONTEND_TEMPLATE

.. setting::
    :name: ERROR_403_TEMPLATE
    :path: lona.default_settings.ERROR_403_TEMPLATE

.. setting::
    :name: ERROR_404_TEMPLATE
    :path: lona.default_settings.ERROR_404_TEMPLATE

.. setting::
    :name: ERROR_500_TEMPLATE
    :path: lona.default_settings.ERROR_500_TEMPLATE

.. setting::
    :name: TEMPLATE_EXTRA_CONTEXT
    :path: lona.default_settings.TEMPLATE_EXTRA_CONTEXT

.. setting::
    :name: TEMPLATE_EXTRA_FILTERS
    :path: lona.default_settings.TEMPLATE_EXTRA_FILTERS

    .. note::

        Added in 1.8.4

    All filters defined in this dictionary will be added to the Jinja2
    templating environment.

    **More Information:** `Custom Jinja2 Filters <https://jinja.palletsprojects.com/en/3.0.x/api/#writing-filters>`_

Static Files
------------

.. setting::
    :name: STATIC_DIRS
    :path: lona.default_settings.STATIC_DIRS

.. setting::
    :name: STATIC_URL_PREFIX
    :path: lona.default_settings.STATIC_URL_PREFIX

.. setting::
    :name: STATIC_FILES_SERVE
    :path: lona.default_settings.STATIC_FILES_SERVE

.. setting::
    :name: STATIC_FILES_STYLE_TAGS_TEMPLATE
    :path: lona.default_settings.STATIC_FILES_STYLE_TAGS_TEMPLATE

.. setting::
    :name: STATIC_FILES_SCRIPT_TAGS_TEMPLATE
    :path: lona.default_settings.STATIC_FILES_SCRIPT_TAGS_TEMPLATE

.. setting::
    :name: STATIC_FILES_ENABLED
    :path: lona.default_settings.STATIC_FILES_ENABLED

.. setting::
    :name: STATIC_FILES_DISABLED
    :path: lona.default_settings.STATIC_FILES_DISABLED


Client
------

.. setting::
    :name: CLIENT_DEBUG
    :path: lona.default_settings.CLIENT_DEBUG

.. setting::
    :name: CLIENT_VIEW_START_TIMEOUT
    :path: lona.default_settings.CLIENT_VIEW_START_TIMEOUT

.. setting::
    :name: CLIENT_INPUT_EVENT_TIMEOUT
    :path: lona.default_settings.CLIENT_INPUT_EVENT_TIMEOUT

.. setting::
    :name: CLIENT_PING_INTERVAL
    :path: lona.default_settings.CLIENT_PING_INTERVAL

    .. note::

        Added in 1.7.4

    To disable ping messages set to ``0``.

Sessions
--------

.. setting::
    :name: SESSIONS
    :path: lona.default_settings.SESSIONS

.. setting::
    :name: SESSIONS_KEY_GENERATOR
    :path: lona.default_settings.SESSIONS_KEY_GENERATOR

.. setting::
    :name: SESSIONS_KEY_NAME
    :path: lona.default_settings.SESSIONS_KEY_NAME

.. setting::
    :name: SESSIONS_KEY_RANDOM_LENGTH
    :path: lona.default_settings.SESSIONS_KEY_RANDOM_LENGTH


Views
-----

.. setting::
    :name: FRONTEND_VIEW
    :path: lona.default_settings.FRONTEND_VIEW

.. setting::
    :name: INITIAL_SERVER_STATE
    :path: lona.default_settings.INITIAL_SERVER_STATE

    .. note::

        Added in 1.10.1

    This dict, if present, is copied to ``server.state``.
    This is a convenient way to define or load server state on startup without
    the need to write a specific middleware.

Error Views
-----------

.. setting::
    :name: ERROR_403_VIEW
    :path: lona.default_settings.ERROR_403_VIEW

.. setting::
    :name: ERROR_404_VIEW
    :path: lona.default_settings.ERROR_404_VIEW

.. setting::
    :name: ERROR_500_VIEW
    :path: lona.default_settings.ERROR_500_VIEW


Middlewares
-----------

.. setting::
    :name: MIDDLEWARES
    :path: lona.default_settings.MIDDLEWARES


Shell
-----

.. setting::
    :name: COMMANDS
    :path: lona.default_settings.COMMANDS


Testing
-------

.. setting::
    :name: TEST_VIEW_START_TIMEOUT
    :path: lona.default_settings.TEST_VIEW_START_TIMEOUT

.. setting::
    :name: TEST_INPUT_EVENT_TIMEOUT
    :path: lona.default_settings.TEST_INPUT_EVENT_TIMEOUT

Server
------

.. setting::
    :name: AIOHTTP_CLIENT_MAX_SIZE
    :path: lona.default_settings.AIOHTTP_CLIENT_MAX_SIZE

    .. note::

        Added in 1.10.2

    This value is used to set the ``client_max_size`` value for the aiohttp server.
    It defines the maximum body size of a post request accepted by the server.
    See
    `aiohttp documentation <https://docs.aiohttp.org/en/stable/web_reference.html#aiohttp.web.Application>`_
    for details.
    The default value is set to the aiohttp default of ``1024**2`` Bytes.
