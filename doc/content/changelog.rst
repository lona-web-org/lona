toctree: False
search_index_weight: -10
is_template: False


Changelog
=========


.. changelog-header:: 1.16.2 (2024-03-25)

Bugfixes
~~~~~~~~

* Client & Client2

  * Multiple browser history bugs were fixed


.. changelog-header:: 1.16.1 (2023-11-28)

Changes
~~~~~~~

* Buckets for file uploads were added

* Middlewares

  * ``handle_http_request`` hook was added
  * ``on_view_stop`` hook was added
  * ``on_view_cleanup`` hook was added

* Requests

  * ``Request.id`` was added


.. changelog-header:: 1.16 (2023-10-20)

Changes
~~~~~~~

* Views

  * All internal views use response classes instead of dict responses now
  * dict based responses issue deprecation warnings now
  * ``context`` in ``TemplateResponse`` and ``TemplateStringResponse`` are
    optional now

* Server

  * Default host and port now can be set using the environment variables
    ``LONA_DEFAULT_HOST`` and ``LONA_DEFAULT_PORT``.

  * Live reload was added (``--live-reload``)

* Frontend

  * Auto reconnect was added

* HTML

  * ``lona.html.RadioButton`` and ``lona.html.RadioGroup`` were added


Bugfixes
~~~~~~~~

* Client & Client2

  * Form submit in interactive views was fixed

    * Previously, the ``onsubmit`` handler crashed because of an reference
      error

* Client2

  * Call stack limit problems in node cache were fixed

    * Previously, the rendering of Client2 would crash when too many nodes
      were removed at the same time


.. changelog-header:: 1.15 (2023-07-20)

Changes
~~~~~~~

* Python

  * Support for Python 3.7 was dropped

    * Python 3.7 is `end of life <https://endoflife.date/python>`_ since
      June of 2023

* Client2

  * A check for unsupported node types was added

    * Previously, the rendering engine would just crash with an cryptic error
      message, when attempting to render an unsupported node type

* HTML

  * ``Node.nodes`` accepts node lists now

    * Previously, the list of sub nodes of a node could only be reset with a
      list or a tuple. Code like ``div2.nodes = div1.nodes`` created a
      ``TypeError``.

  * ``Node.widget_data`` now can be initialized via the constructor or by
    setting ``WIDGET_DATA`` in the class scope

  * ``lona.html.parse_html`` was added

    * Previously, ``lona.html.HTML`` was used to parse HTML strings. Because
      ``lona.html.HTML`` works like a normal node and is mainly used to
      communicate that a function returns HTML, the community decided that
      these two concerns should be split up.

     ``lona.html.HTML`` is no deprecated for HTML string parsing, and this
     feature will be removed from it in version 2.

* Logging

  * Obsolete information when logging ``lona.errors.ClientError`` exceptions
    were removed

    * Previously, a raised ``lona.errors.ClientError`` was logged two times.
      Once by the worker, that received the error, and a second time by the
      general logging setup of Lona. The first log entry contained the
      JavaScript traceback, raised by the browser, the second log entry
      contained the full Python traceback from the server side.

      The second log entry did not contain any meaningful information, since
      the Python traceback only contained Lona framework code, never
      application code.

      The second log entry was removed, because it made these errors only
      harder to read.


Bugfixes
~~~~~~~~

* collect-static

  * Handling of deeply nested directories was fixed

    * Previously, the ``collect-static`` command crashed when a static directory
      was deeply nested but contained only one file

* HTML

  * Node comparisons between nodes and legacy widgets was fixed

    * Previously, node comparisons, using ``==``, crashed when one of the two
      nodes was a legacy widget

* Client2

  * Moving an already rendered node was fixed

    * Previously, client2 crashed when an already rendered node was moved by
      appending or inserting it twice within the same HTML tree.

      .. code-block:: python

          moving_node = Div('node 3')

          html = HTML(
              Div(
                  'node 1',
                  moving_node,
              ),
              Div('node 2'),
          )

          self.show(html)

          html[1].append(moving_node)

          self.show(html)  # resulted in: ERROR  lona.view_runtime  client error raised: node with id 952 is already cached


.. changelog-header:: 1.14 (2023-05-22)

Changes
~~~~~~~

* Templates

  * Support for favicons was added to the default frontend template
    ``lona/frontend.html``

* HTML

  * Performance of ``Node.append()`` was improved

    * Previously, ``Node.append()`` used ``NodeList.index()`` internally,
      which called ``Node._serialize()`` which is an expensive operation.

      ``Node.append()`` now calculates the index of the appended node itself,
      which is much faster.

  * Performance of ``Node.__eq__()`` was improved

    * Previously, ``Node.__eq__()`` used ``Node._serialize()`` which is an
      expensive operation. Now ``Node.__eq__()`` checks all attributes of two
      nodes individually, trying to find a difference as soon as possible.

  * ``Node.tag_name`` and ``Node.widget`` are read-only now

    * Re-writing of these properties was never supported, so it should not be
      possible to write them, to prevent confusion.

* State

  * ``State.to_json()`` was added

* Sessions

  * ``SESSIONS_REUSE`` setting was added

    * When set to ``False`` the session middleware will create a random session
      key for every new connection. This is useful for debugging multi-user
      views.

* Client 1&2

  * Support for reconnecting without creating a window was added

    * Previously, when implementing auto-reconnect, the client would reopen the
      websocket connection, and in the case of success reload the tab. This
      reload is crucial to ensure a connect and a reconnect result in the same
      user experience, but has the side effect of accessing the same view
      twice. This created problems when debugging or reading the server logs.

      To account for that, the option ``create_window`` was added to
      ``LonaContext.reconnect()``, which is set to ``true`` by default.

* Channels

  * Channels were added

    * Channels are the successor to View Events, and are the new mechanism for
      soft real-time communication and multi-user features.

* Views

  * View Events are deprecated now in favor of Channels


Bugfixes
~~~~~~~~

* Client 1&2

  * Index of inserted nodes was fixed

    * Previously, the rendering engine used ``Element.children`` to insert
      newly rendered nodes. This only works correctly when the target node only
      contains elements and no text nodes, because ``Element.children`` only
      contains references to child elements, in contrast to
      ``Element.childNodes`` which contains child elements and child text
      nodes. The usage of only this subset of nodes lead to incorrect indices,
      and nodes ending up in wrong order, in some cases.

* Client 2

  * Crashes while rendering node list slices were fixed

    * Previously, the rendering engine could crash when a slice of
      ``Node.nodes`` was re-rendered. This was due incorrect node cache
      cleaning on the client, and was fixed by cleaning the cache after every
      node-reset-operation.


.. changelog-header:: 1.13 (2023-04-01)

Changes
~~~~~~~

* Templates

  * ``viewport`` was set in ``lona/frontend.html``, to improve scaling on
    mobile devices

* HTML

  * All missing HTML5 nodes, but missing inputs, were added to the standard
    library

    Reference: https://developer.mozilla.org/en-US/docs/Web/HTML/Element

  * Support for XML namespaces was added, to add support for SVG rendering

  * Support for non-standard CSS-properties was added

    * Frameworks like `bonsai.css <https://www.bonsaicss.com/>`_ use
      non-standard CSS-properties like ``--maxw:10px``.

  * ``lona.html.HTML`` parses element attributes case-sensitive now

    * Previously, ``lona.html.HTML`` converted all element attributes to
      lower-case. This is fine for XHTML, but leads to issues when parsing
      SVGs since some of the attributes in the SVG namespace are
      case-sensitive.

  * ``lona.html.RawHTML`` was added


Bugfixes
~~~~~~~~

* HTML

  * Parsing of single nodes in HTML-strings was fixed

    * Previously, when parsing HTML-strings, that contained only one node, the
      resulting node was no root node, but it had a parent node set, that was
      out of scope.

      This lead to crashes, because Lona refuses to render nodes on the
      top-level, which are no root-nodes.

* Client

  * Backwards compatibility with legacy frontend widget API was fixed


.. changelog-header:: 1.12.4 (2023-03-19)

Bugfixes
~~~~~~~~

* Views

  * TypeError in ``View.sleep()`` on Python 3.11 was fixed

    * ``View.sleep()`` uses ``View._await_sync`` internally, which previously
      used ``asyncio.wait`` with coroutines. Since Python 3.11,
      ``asyncio.wait`` forbids coroutines, therefore Lona now converts its
      them to asyncio tasks before calling ``asyncio.wait``.

      https://docs.python.org/3/library/asyncio-task.html#waiting-primitives

* HTML

  * Duplicate node reset patches were fixed

    * ``NodeList.reset()`` gets called with a list of nodes when the
      ``Node.nodes`` property gets set. ``NodeList.reset()`` then clears its
      node list and creates a ``lona.protocol.OPERATION.RESET`` patch.

      Previously, the code falsely create a patch for every new node, that
      contained all following nodes. That resulted in a list of patches that
      would override each other on the client.

      This was no problem in the past, because the client had no checks before
      whether a node was already sent by the server, and because the patches
      overwrote each other, the HTML end-result always was correct.

  * Incorrect node wrapping on client2 when parsing HTML strings was fixed

    * Previously, when client2 was used, ``lona.html.HTML`` used
      ``lona.html.HTML`` (itself) to parse given HTML-strings. On client2,
      ``lona.html.HTML`` wraps all nodes on the top-level of the parsing
      result, if the parser returned more than one root node.

      This combination resulted in incorrect node wrapping, not only on the
      top-level, but also in sub-trees.

* Client

  * Rendering of HTML symbols was fixed

    * https://www.w3schools.com/html/html_symbols.asp

  * The ``Widget.deconstruct`` was fixed

    * Previously, ``Widget.deconstruct`` only ran when a node got orphaned
      after a node clearing operation, and got collected by the
      rendering-engine. It did not run, when a single node got removed from the
      client.

  * Relative URL resolving was fixed

    * Previously, the resolving of relative URLs was a custom implementation,
      which had multiple weird quirks, and behaved differently than the
      browsers implementation. That was confusing, because redirects, issued by
      the server, sometimes resulted in slightly different URLs than their
      link-counterparts.

      The client uses the browsers URL resolving implementation now, to ensure
      that client-side and server-side issued redirects behave the same.


Changes
~~~~~~~

* Client

  * The ``WidgetData`` class was added to make room for high-level API like
    ``WidgetData.set`` or ``WidgetData.get`` in the future

  * References to the Lona window, the root node, and the widget data of a
    widget, got added to ``Widget.constructor`` calls, to replace
    ``Widget.setup`` in the future

  * ``Widget.onDataUpdated`` was added to replace ``Widget.data_updated`` in
    the future

  * ``Widget.destroy`` was added to replace ``Widget.deconstruct`` in the
    future

  * A reference to the Lona window was added to the ``LonaWindowShim`` class


.. changelog-header:: 1.12.3 (2023-02-12)

Bugfixes
~~~~~~~~

* JavaScript client crashes on iPhone 6 and iPad mini 2 were fixed

  * Previously, the client used JavaScript public field declarations in the
    Lona namespace class. Public field declarations are not supported in
    Safari versions lower 14.1 and iPhone 6 and iPad mini 2 are running
    version 12.


.. changelog-header:: 1.12.2 (2023-02-10)

Bugfixes
~~~~~~~~

  * Handling of ``View.is_daemon`` was fixed

    * The problem, described in 1.12.1, was not fixed entirely before. The
      server still did not remove daemonized views, that were stopped,
      correctly in all cases


.. changelog-header:: 1.12.1 (2023-02-10)

Bugfixes
~~~~~~~~

* Views

  * Handling of redirects and HTTP redirects from event handlers were fixed

    * 1.12 introduced ``lona.responses.AbstractResponse`` as new data structure
      for responses, but did not update all type checks in the event handler
      code

  * Handling of feature flag ``STOP_DAEMON_WHEN_VIEW_FINISHES`` was fixed

    * Previously, only ``View.STOP_DAEMON_WHEN_VIEW_FINISHES`` worked,
      ``settings.STOP_DAEMON_WHEN_VIEW_FINISHES`` had no effect

  * Handling of ``View.is_daemon`` was fixed

    * 1.12 changed the checks, if a view should be removed from the server, to
      make short running deamon-views possible.

      When ``View.STOP_DAEMON_WHEN_VIEW_FINISHES`` was set to ``False`` and
      ``View.is_daemon`` to ``True``, the view did not get removed from the
      server when the user closed the tab, and got reconnected to the same
      view, when reopening the tab.

      When ``View.STOP_DAEMON_WHEN_VIEW_FINISHES`` was set to ``True``, which
      is the default, and ``View.is_daemon`` also to ``True``, the view should
      be removed from the server, when it finishes, and the tab gets closed,
      but instead the view remained on the server, but was not reconnected when
      reopening the tab.

      That meant that the server created a new view on every access of a page,
      and did neither reuse or close it, so they built up indefinitely.


.. changelog-header:: 1.12 (2023-02-07)

Changes
~~~~~~~

* Python

  * Support for Python 3.11 was added

  * Packaging using ``pyproject.toml`` was added

    * A ``pyproject.toml`` was added, to fix two problems with the current
      packaging at once:

      1. Deprecation warnings

      The previous setup, using a legacy ``setup.py``, produced this warning
      since pip 23.0:

      ::

        DEPRECATION: lona is being installed using the legacy 'setup.py install'
        method, because it does not have a 'pyproject.toml' and the 'wheel' package
        is not installed. pip 23.1 will enforce this behaviour change. A possible
        replacement is to enable the '--use-pep517' option. Discussion can be found
        at https://github.com/pypa/pip/issues/8559

      2. Problems with package data

      On some systems, package data like the JavaScript client or templates
      are missing, when Lona is installed using the git URL:

      ::

        pip install git+https://github.com/lona-web-org/lona.git

* Client

  * The client code was moved into the prefix ``/client/``

    * The client URL was changed from ``/static/_lona/lona.js`` to
      ``/static/_lona/client/lona.js``, to make room for the new client
      implementation of Lona 2. It is planed to
      support both clients until Lona 2 gets released.

  * Client 2 was added

    * This release adds the first version of client 2, which will be the
      implementation for Lona 2.

      Client 2 is a completely separate code base, to be fully
      backwards-compatible, until Lona 2 gets released.

      The new client can be enabled, by setting the feature flag
      ``CLIENT_VERSION`` to ``2`` in the settings (default is ``1``).
      On startup the server calls a new added method
      ``lona.compat.set_client_version`` which sets the configured version in
      the environment variable ``LONA_CLIENT_VERSION``.

      This extra step through the environment is necessary, to communicate to
      ``lona.html`` types, which client version is running, since they have no
      access to the settings.

      The currently configured client version can be checked using
      ``lona.compat.get_client_version()``.

* Client 2

  * Support for legacy widget API was dropped

    Lona 1 defines two types of nodes: Nodes that can be rendered in the
    browser (text nodes and elements), and collections of nodes that can be
    rendered (widgets). This distinction was made to make components (for
    example a pop-up component) with multiple root nodes possible.

    This feature was useful in some cases but brought much complexity and error
    potential into the JavaScript client. Also the implications of enforcing
    every component to have exactly one root node, are not big enough to
    justify this level of complexity.

    All widget rendering code was removed from client 2 and ``lona.html.HTML``
    was updated to return a node instead of a widget when client 2 gets
    used.

* HTML

  * Select2 was added

    * Previously, the API of ``html.Select`` was quite confusing because its
      main control mechanism over its options and their values were
      ``html.Select.value`` and ``html.Select.values``. ``values`` was
      represented as a list of tuples, which got parsed into ``html.Option``
      objects with their values and attributes set.
      Values always got converted to strings, which is the correct behavior,
      from a browsers perspective, but it was surprising and inconvenient.

      A new select implementation, named ``lona.html.Select2``, with a more
      intuitive API, that preserves the original values of options, was added.

      For compatibility reasons, ``html.HTML`` still uses ``html.Select``,
      when parsing HTML strings.
      The new implementation can be used by setting the feature flag
      ``USE_FUTURE_NODE_CLASSES`` to ``True`` in the settings (default is
      ``False``).

  * The parser now uses ``value`` properties instead of setting them as
    attribute

    * ``value``, most of the time, is used in nodes like ``Select`` or
      ``TextInput``, and is implemented as a high-level property.

      Previously, ``value`` got treated as an node attribute.
      The parsing code was changed to treat ``value`` as key word
      argument of the node class, so all high-level properties get used.
      If a node does not implement a high-level property for ``value``, the
      node base-class falls back to setting ``value`` as an attribute.

* Views

  * Response classes were added

    Previously, Lona views used special dictionaries as responses, instead of
    proper response classes like any other Python web framework.

    This is a design that was part of Lona since the very beginning. In the
    early days of this framework, views were simple functions, that needed
    almost no imports. The idea was to use a Python standard data structure,
    so no classes had to be imported, and no response class names had to be
    remembered.

    This was a horrible idea, and lead to horrible code, namely the
    ``ResponseParser`` code. Because the dictionaries could contain any key,
    they had to be parsed.

    Response classes, for any type of response Lona supports, and a
    drop-in-replacement for the response parser code, that converts
    dictionaries into responses, were added, to be backwards compatible.

    Response dicts are deprecated now, and will be removed in Lona 2.


Bugfixes
~~~~~~~~

* Handling of overlapping directories got fixed in ``collect-static`` command

  * Previously collect-static crashed, when two static directories contained the
    same sub directory.

    Example:

    ::

      project/static-dir-1/directory/file.txt
      project/static-dir-2/directory/file.txt

    On Python versions after 3.7, this was fixed by setting the
    ``dirs_exist_ok`` flag, in the ``shutil.copytree()`` call in
    collect-static.

      https://docs.python.org/3/library/shutil.html#shutil.copytree

    Because this flag does not exist on Python 3.7, code was added to
    emulates this feature, and a check which implementation should be used.

* aiohttp deprecation warning was fixed

  ::

    .tox/python/lib/python3.8/site-packages/aiohttp/web_protocol.py:451:
    DeprecationWarning: returning HTTPException object is deprecated (#2415)
    and will be removed, please raise the exception instead

* Multiple node caching issues in Client 2 were fixed

  * Previously the rendering code sometimes accessed the node cache directly,
    instead of using ``_get_node()``. JavaScript (being JavaScript) returned
    ``undefined`` if no node with the given node id exists.
    So, looking up an unknown node id "worked" but the code then crashed when
    trying to patch the retrieved node, which was hard to debug.

    These problems were fixed, by adding a node id check to ``_get_node()``,
    which throws an exception, when an unknown node id was given, and all old
    code, that accessed the node cache directly, was removed.


.. changelog-header:: 1.11 (2023-01-09)

Changes
~~~~~~~

* HTML

  * An initial value for ``Node.state`` now can be set while creating a node,
    using ``Node(state={})``

  * The ``AbstractNode`` class supports comparisons now

    .. code-block:: python

        >>> Div() == Div()            # True
        >>> Div() is Div()            # False
        >>> Div(a=1) == Div()         # False
        >>> Span() == Div()           # False
        >>> Div(Div()) == Div(Div())  # True

  * ``index()`` in lists, in widget data was fixed

    * Due a copy-paste issue, ``index()`` in lists, in ``WidgetData`` objects,
      called ``count()`` instead of ``index()``, in their inner data
      structures, in all Lona versions, prior to 1.11.

* Input Events

  * ``target_node`` attribute was added to the ``InputEvent`` class

    * In JavaScript, when an event listener for a click event is attached to a
      node, the resulting event can be originally issued by one of its child
      nodes, but catched by the node that defined the event listener.

      Previously, when setting up events on a Lona node, there was no way to
      determine if an event was issued by this exact node or by one of its
      child nodes.

      This resulted in problems when using clickable nodes inside clickable
      nodes, which can be a valid use-case, for example for clickable backdrops
      that contain buttons.

      To solve this problem, a new attribute, named ``target_node``, was added
      to the ``InputEvent`` class, which is the equivalent to ``event.target``
      in JavaScript.

* Testing

  * ``lona.pytest.LonaContext.debug_interactive``

    * stdin and stdout capturing is now disabled during runtime

      * ``lona.pytest.LonaContext.debug_interactive`` starts a rlpython shell
        that reads and writes to stdin and stdout, which are captured by pytest
        by default.

        Previously this had to be disabled by hand, by setting ``-s`` in the
        pytest command line (or respective pytest config variable) to make the
        shell work.

        ``lona.pytest.LonaContext.debug_interactive`` now disables pytests
        capturing before rlpython starts, and reenables it after rlpython
        stops.

* Views

  * Daemonizing support for short running views was added

    * Previously daemonizing required views their ``handle_request()`` method
      to run as long as they wanted to be daemonized, blocking one thread for
      the entire lifetime of the view.

      The view runtime checks got changed, so that daemonized views can be
      finished without getting removed from the server.

      Previously a view got daemonized by calling ``LonaView.daemonize()`` and
      "undaemonized" and removed from the server by simply returning from
      ``handle_request()``. ``LonaView`` now has a new boolean property, called
      ``is_daemon``, which enables or disables if a view should be a daemon or
      get removed from the server.

      Because this potentially changes the flow of existing user application
      code, the new behavior is only active when
      ``LonaView.STOP_DAEMON_WHEN_VIEW_FINISHES`` is set to ``False``, which
      is set to ``True`` by default.


Bugfixes
~~~~~~~~

* HTML

  * Multiple tree unmounting and loop-detection issues were fixed

    * Lona nodes have to be unique, because they are meant to represent exactly
      one node in the browser DOM. This means, when a node gets mounted into a
      node tree, it has to be unmounted at its previous parent node tree, if
      present.

      Previously this mechanism was flawed, and there were scenarios in which a
      node could appear in multiple node trees, or appear multiple times in the
      same node tree. In these cases the loop detection sometimes ended up in
      an endless loop.

* Client

  * Handling of the default Lona window was fixed

    * In Lona protocol, window ids are set by the client. The client holds an
      id counter starting at ``1`` and increments it for every new window. If
      reconnect is configured, like shown in
      ``https://lona-web.org/1.x/cookbook/auto-reconnect.html``, the counter
      gets incremented on every reconnect.

      ``LonaContext`` defines
      ``patch_input_events(root_node_selector, window_id)``, which is meant to
      patch the input events on global navigation, or search-bars.
      If no ``window_id`` is given, ``LonaContext.get_default_window()`` is
      called, which previously always tried to return a window with the id
      ``1``. This hard coded value worked until the first reconnect. After
      that, ``LonaContext.get_default_window()`` returns ``undefined`` and this
      JavaScript exception got thrown, when running
      ``LonaContext.patch_input_events()``:

      .. code-block::

          Uncaught TypeError: Cannot read properties of undefined (reading '_input_event_handler')
              at context.js:98:21
              at NodeList.forEach (<anonymous>)
              at LonaContext.patch_input_events (context.js:97:41)
              at (index):125:24
              at LonaContext._run_connect_hooks (context.js:131:13)
              at _ws.onopen (context.js:324:31)

      This issue was fixed, by changing ``LonaContext.get_default_window()`` to
      always return the window with the lowest window id.

  * Implementation of ``id_list.remove()`` was fixed

    * The previous, client side, implementation of ``Node.id_list.remove()``
      did not remove a specific id from the id list, but removed the last
      id in the list.

  * Class attribute clearing was fixed

    * Previously the class attribute was cleared by setting its value to an
      empty string, but that does not remove it completely. Now, the attribute
      gets removed using ``Node.removeAttribute()`` in JavaScript.

* Input Events

  * Event bubbling in the browser client was fixed

    * Previously the browser client did not stop the propagation of events
      that were already send to the server. That meant that events continued
      bubbling up the tree, getting catched and send to the server multiple
      times.

      This issue was fixed, by adding an ``event.stopPropagation`` call to
      all intern input event listeners, to stop already catched input events
      from bubbling up any further.

* Testing

  * ``lona.pytest.LonaContext.debug_interactive``

    * ``locals`` vs. ``global`` issue was fixed

      * All rlpython versions before 0.9 made a distinction between globals and
        locals, which resulted in scoping issues. In

        .. code-block::

          128ff5bc9278 ("repl: fix locals and globals issues")
          (https://github.com/fscherf/rlpython/commit/128ff5bc9278314f3f44e53773a1dfc4f4229ca6)

        globals and locals were consolidated to replicate the behavior of the
        Python standard REPL more closely.

        The call into the rlpython API was changed, to accommodate for the
        upstream fix.


.. changelog-header:: 1.10.5.1 (2022-12-12)

Bugfixes
~~~~~~~~

* Packaging

  * A ``ModuleNotFoundError``, that raised on some systems while installing
    Lona, was fixed

    * Previously the package mechanism assumed that all dependencies are fully
      installed, before Lona gets installed. This assumption seems to be
      incorrect on some systems.


.. changelog-header:: 1.10.5 (2022-12-05)

Changes
~~~~~~~

* HTML

  * Frontend Widget capabilities were added to the abstract node class

    * Previously only nodes, subclassing ``lona.html.Widget``, could define a
      frontend widget. Now, any node, besides text nodes, can do so.

      This is in preparation of making the widget API obsolete at first, and
      removing it entirely in Lona2.


Bugfixes
~~~~~~~~

* HTML

  * Handling of non-string attributes like ``True`` was fixed in string
    representations

    * Previously code like ``str(Option(bubble_up=True))`` crashed

* collect-static

  * A regression, added in 1.10.2, was fixed


.. changelog-header:: 1.10.4 (2022-09-26)

Changes
~~~~~~~

* Client

  * Python based pre compiler was replaced with JavaScript ES06 imports

    * The sole reason for the client pre compiler was to add Python constants
      and Javascript imports to the vanilla Javascript client implementation.

      Since all major browsers support ES06 imports now, and Python constants
      can also resolved in the templating stage, the client pre compiler was
      removed.

Bugfixes
~~~~~~~~

* Client

  * Node caching problem was fixed

    * Previously the node cache got cleaned out after every rendering patch
      that was applied. In some cases that resulted in situations in which
      nodes got cleaned out of the cache before they were applied to the Dom.

      When a patch came in, for a node that was not present in the node cache,
      the client crashed.

      This issue was fixed by removing the cash clear calls after every patch
      and add one call after an entire patch stack.


.. changelog-header:: 1.10.3 (2022-08-12)

Bugfixes
~~~~~~~~

* Fix client crashes

  * ``1.10.2`` introduced some uninitialized variable and variable name issues
    that caused occasional crashes


.. changelog-header:: 1.10.2 (2022-07-31)


Changes
~~~~~~~

* Server

  * Add setting to set aiohttp ``client_max_size``

* Client

  * Window shortcuts were added

    * In most applications Lona has only one window.
      The Shortcuts ``window.get_default_window()`` and ``window.run_view()``
      were added to access this first window as the default window.


Bugfixes
~~~~~~~~

* Client

  * Window id reuse was fixed

    * Previously Lona generated a new window id by incrementing the current
      window count. This lead to potential reuse of ids, when a window got
      removed


.. changelog-header:: 1.10.1 (2022-04-03)


Changes
~~~~~~~

* Server State

  * Server State can pre set using ``settings.INITIAL_SERVER_STATE`` now


.. changelog-header:: 1.10 (2022-03-21)


Changes
~~~~~~~

* Templating

  * The shortcut ``Lona.settings`` to ``server.settings`` was added
  * The shortcut ``Lona.state`` to ``server.state`` was added
  * Support for top level imports like ``json`` was added

    * Previously template imports like ``{% Lona.import('json') %}`` failed

* Client

  * Debug mode was added

    * When ``settings.CLIENT_DEBUG`` is set to ``True`` Lona recompiles the
      client on every request and serves all library files seperately to make
      Chrome Inspector work as expected

* Server State

  * Support for equal comparisons was added

    * Previously operations like ``server.state['foo'] == ['foo', 'bar']``
      were not supported

* HTML

  * Add ``AbstractNode.state``

* Server

  * ``route_name`` argument was added to ``Server.get_view_class()``
  * ``route_name`` argument was added to ``Server.get_views()``


Bugfixes
~~~~~~~~

* Views

  * Page titles on daemonized views were fixed

    * Previously the the page title was send only once on view start and was
      not resend when reconnecting to a view

* Server State

  * Boolean typecasts were fixed

* HTML

  * node static file discovery was fixed using
    `PEP 487 <https://www.python.org/dev/peps/pep-0487/>`_

    * Previously node static file discovery used ``__subclasses__()``. This
      method sometimes failed unreproducible, while running the test suite in
      CI. It seems this problem has something to do with multi-threading, which
      gets used heavily in Lona.


Breaking Changes
~~~~~~~~~~~~~~~~

* Templating

  * ``Lona.resolve_url`` was renamed to ``Lona.reverse``

    * This makes naming across Lona more consistent

* Settings

  * ``CLIENT_RECOMPILE`` was replaced with ``CLIENT_DEBUG``
  * ``STATIC_FILES_CLIENT_URL`` was removed

* Static Files

  * Lona client files get served using the URL prefix ``_lona/`` now


.. changelog-header:: 1.9 (2022-01-28)


Changes
~~~~~~~

* Input events

  * ``FOCUS`` and ``BLUR`` were added

* Server

  * ``LonaServer.project_root`` was added
  * ``LonaServer.template_dirs`` was added
  * ``LonaServer.static_dirs`` was added
  * ``LonaServer.get_views`` was added

* Testing

  * Pytest based testing was added


Bugfixes
~~~~~~~~


* Packaging

  * Import errors during installation were fixed

    * Previously an import error stating that ``typing-extensions`` is not
      installed could occur while installing the Lona package

* HTML

  * Quoting in Python representations were fixed

    * Previously representations looked like this:
      ``<input data-lona-node-id="1" type=&quot;checkbox&quot; />``

* Scripts

  * Return value of ``app.route`` decorator was fixed

    * Previously the decorator returned nothing which overwrote the given
      view class with ``None``



Breaking Changes
~~~~~~~~~~~~~~~~

* Server

  * ``LonaServer.websockets`` is a private attribute now
  * ``LonaServer.templating_engine`` is a private attribute now
  * ``LonaServer.router`` is a private attribute now
  * ``LonaServer.middleware_controller`` is a private attribute now
  * ``LonaServer.view_loader`` is a private attribute now
  * ``LonaServer.response_parser`` is a private attribute now
  * ``LonaServer.view_runtime_controller`` is a private attribute now
  * ``LonaServer.client_pre_compiler`` is a private attribute now
  * ``LonaServer.static_file_loader`` is a private attribute now
  * ``LonaServer.settings_paths`` is a read only property now


.. changelog-header:: 1.8.5 (2021-12-15)


Bugfixes
~~~~~~~~

* Import errors on non-Unix systems were fixed

  * Previously the package ``syslog`` got imported on startup without proper
    error handling.


.. changelog-header:: 1.8.4 (2021-12-05)


Changes
~~~~~~~

* Templates

  * Support for custom Jinja2 filters was added


.. changelog-header:: 1.8.3 (2021-11-24)


Changes
~~~~~~~

* Shell Commands

  * ``logging syslog priorities`` was added to ``%lona_info``

* Logging

  * Command line option ``--syslog-priorities=no|always|auto`` was added

* Error Views

  * ``lona.NotFoundError`` was added
  * ``lona.LonaApp.error_403_view`` was added
  * ``lona.LonaApp.error_404_view`` was added
  * ``lona.LonaApp.error_500_view`` was added


Bugfixes
~~~~~~~~

* Logging

  * Check if running in a systemd unit was fixed

    * On modern Linux desktop systems the desktop environment is often started
      within a systemd unit. In these setups ``JOURNAL_STREAM`` is often set in
      every shell. Therefore this check often yielded false positive results.


.. changelog-header:: 1.8.2 (2021-11-22)


Changes
~~~~~~~

* Logging

  * Support for syslog priorities was added


.. changelog-header:: 1.8.1 (2021-11-17)


Bugfixes
~~~~~~~~

* HTML

  * Memory issues in widget data updates were fixed


.. changelog-header:: 1.8 (2021-11-11)


Breaking Changes
~~~~~~~~~~~~~~~~

* ``LonaView.on_shutdown`` was removed

  * ``LonaView.on_shutdown`` is deprecated and got replaced by
    ``LonaView.on_stop`` and ``LonaView.on_cleanup``

* ``LonaView.iter_objects`` was removed

  * ``LonaView.iter_objects`` is deprecated and got replaced by
    view events

* ``LonaView.embed_shell`` and ``server.embed_shell`` were removed

  * ``embed_shell`` never worked like an end-user would expect, because it
    always runs in it's own scope, and not in the scope of the caller of the
    method. The better way to do this is to use rlpython directly


Changes
~~~~~~~

* HTML

  * ``lona.html.NumberInput`` was added
  * ``lona.html.NodeList.index`` was added
  * ``lona.html.NodeList.extend`` was added
  * ``lona.html.HTML.index`` was added
  * ``lona.html.HTML.extend`` was added

* Routing

  * Route names are unique now. If a name gets reused a warning gets logged

* Views

  * Support for binary responses was added to non-interactive views
  * Support for custom HTTP headers was added to non-interactive views


Bugfixes
~~~~~~~~

* Client

  * Scrolling issues were fixed

    * Previously when the HTML of a view was scrolled down and a new view
      started, the HTML of the new view started scrolled to the previous scroll
      position. This only happened if a ``height`` CSS role was applied to the
      body or the Lona window.

* Routing

  * Handling of optional trailing slashes was fixed

    * Previously routes that ended with an argument and an optional slash
      (``Route('/foo/<bar>(/)')``) couldn't be routed or reverse matched

  * The first argument of ``Server.reverse`` was changed from ``name`` to
    ``route_name``

    * Previously routes with an argument named ``name`` couldn't be reverse
      matched because of this naming clash


.. changelog-header:: 1.7.6 (2021-11-01)


Changes
~~~~~~~

* aiohttp

  * Support for aiohttp 3.8 was added


Bugfixes
~~~~~~~~

* Server

  * Slow downs when removing connections were fixed

    * Previously connections were removed directly on the ioloop which pulles
      a HTML lock implicitly. This meant that, in worst case scenarios, the
      server was locked until a view released its lock.


.. changelog-header:: 1.7.5 (2021-10-20)


Bugfixes
~~~~~~~~

* Views

  * Handling of top level nodes was fixed

    * Previously a node could not get associated with an input event if it was
      on the first level of a HTML tree

  * Cleanup of non-interactive view runtimes was fixed

    * Previously non-interactive view runtimes never got removed from memory

* Protocol

  * Duplicate method status codes were fixed

    * Previously ``METHOD.PING`` had the same value as
      ``INPUT_EVENT_TYPE.CLICK`` and ``METHOD.PONG`` had the same value as
      ``INPUT_EVENT_TYPE.CHANGE``

* HTML

  * The return value of ``Select.value`` was fixed

    * Previously ``Select.value`` would always return the first option if no
      option is selected, which is only correct if ``multiple`` is set to
      ``False``


.. changelog-header:: 1.7.4 (2021-10-13)


Changes
~~~~~~~

* Deprecations

  * ``LonaView.iter_objects()`` is now deprecated and will be removed in 1.8

    * This method is replaced by the view events API

  * ``LonaView.on_shutdown()`` is now deprecated and will be removed in 1.8

    * This hook has many flaws and special rules when it runs and when not.
      It is replaced by ``LonaView.on_stop()`` and ``LonaView.on_cleanup()``

* Support for Python3.10 was added

* Views

  * ``LonaView.on_stop()`` was added
  * ``LonaView.on_cleanup()`` was added
  * Redirect support was added to ``LonaView.handle_input_event()``
  * Redirect support was added to ``LonaView.handle_input_event_root()``
  * Redirect support was added to ``LonaView.on_view_event()``

* Client

  * Ping messages were added

    * Modern browsers like Chrome close websockets after a preconfigured
      timeout of around five minutes of inactivity to save energy. This can
      lead to all sorts of bad user experience, because all important state is
      part of the view in Lona.


Bugfixes
~~~~~~~~

* html

  * Handling of generators was fixed

    * Previously lines like ``Div(Div() for in range(10))`` did not work


.. changelog-header:: 1.7.3 (2021-10-08)


Changes
~~~~~~~

* views

  * View events were added

* static files

  * Lona now logs an error if static file names are not unique
  * ``LonaView`` classes can define ``STATIC_FILES`` now

* command line

  * Debug mode ``input-events`` was added

* testing

  * ``lona.pytest.eventually`` was added


Bugfixes
~~~~~~~~

* static files

  * All static files are properly sorted now


.. changelog-header:: 1.7.2 (2021-09-28)


Changes
~~~~~~~

* scripts

  * Command line argument parsing was added


Bugfixes
~~~~~~~~

* static files

  * Handling of ``linked=False`` was fixed

    * Previously this flag had no effect

* client

  * Handling of internal links and redirects was fixed

    * Previously link targets like ``.``, ``..`` ``./foo`` or ``foo`` didn't
      work as expected


.. changelog-header:: 1.7.1 (2021-09-21)


Breaking Changes
~~~~~~~~~~~~~~~~

* Support for Python3.6 was dropped

  * Lona uses playwright for testing now and playwright is Python3.7+


Changes
~~~~~~~

* html

  * ``lona.html.HTML`` raises a ``ValueError`` on missing or unexpected end
    tags, while parsing HTML strings, now

* testing

  * The fixtures ``lona_app_context`` and ``lona_project_context`` were added


Bugfixes
~~~~~~~~

* html

  * Typos in ``AttributeList`` error messages were fixed
  * HTML escaping in attributes was fixed

    * Previously values like ``"Times New Roman"`` lead to invalid HTML

  * Handling of boolean attributes in node string representations were fixed

  * Handling of ``interactive`` and ``ignore`` keywords in ``lona.html.A``
    was fixed

  * Parsing of slashes in self closing tags was fixed

* client

  * Rendering of boolean attributes was fixed

    * Previously ``checked=False`` resulted in ``checked`` set to ``true``
      in the browser

  * Handling of external links was fixed

    * Previously external link targets that were used like internal links
      crashed the client and resulted in redirect loop


.. changelog-header:: 1.7 (2021-09-16)


Breaking Changes
~~~~~~~~~~~~~~~~

* html

  * ``==`` now checks if node A ``is`` node B

    * Previously ``==`` checked if node A had equal attributes as node B,
      This caused problems with builtin methods like ``list.index``, which
      resulted in rendering bugs


Bugfixes
~~~~~~~~

* html

  * Parsing of input types was fixed
  * ``Checkbox.value`` has always the type ``bool`` now
  * Parsing of ``TextArea.value`` was fixed


.. changelog-header:: 1.6.1 (2021-09-08)

Bugfixes
~~~~~~~~

* client

  * Handling of boolean attributes was fixed


.. changelog-header:: 1.6 (2021-09-06)

Changes
~~~~~~~

* html

  * ``Node.handle_change()`` now gets called with ``Node.value`` already
    changed in input nodes

    * Previously ``Node.handle_input_event()`` didn't set ``Node.value``
      so a custom ``handle_change()`` handler had to do it itself which
      produced unnecessary boilerplate code

  * ``lona.html.Reset`` was removed

    * This node never worked as expected, also using reset buttons should be
      avoided anyways (Source: `developer.mozilla.org <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/reset>`_)

  * All boolean attributes use empty strings instead of ``'true'`` now

  * All boolean attributes raise a ``TypeError`` now if they get initialized
    with a non-boolean value

  * ``lona.html.Select.multiple`` was added

  * A ``readonly`` property was added to all input nodes

  * ``lona.html.Node`` accepts ``handle_change`` and ``handle_click`` event
    handler in its constructor now

Bugfixes
~~~~~~~~

* html

  * All Python ``in`` checks are thread safe now

  * All boolean attributes (``disabled``, ``checked``, ``multiple`` etc) were
    fixed

    * Previously they were treated as string attributes. When initialized with
      ``False`` (``Button(disabled=False)``) the button was disabled in the
      browser anyway, because the renderer only checks if ``disabled`` is set,
      not its value.

  * Handling of ``id``, ``class`` and ``style`` while parsing HTML using
    ``lona.html.HTML`` was fixed

* client

  * Non node related input events were fixed


.. changelog-header:: 1.5.1 (2021-09-03)

Bugfixes
~~~~~~~~

* html

  * ``html.TextInput.disabled``, ``html.Select.disabled``: These values are
    always bool now

    * Previously these could be a bool or an empty string

  * Unsafe type checks on nodes were fixed

    * This could lead to infinite loops when iterating over nodes before

* input event

  * ``IndexError`` in events, that have no associated node, were fixed

* Javascript client

  * All disconnect hooks are disabled now on page unload

    * Previously all hooks ran when reloading or unloading the page which
      lead to "Server disconnected" error messages in Firefox when leaving the
      page


.. changelog-header:: 1.5 (2021-09-01)

Breaking Changes
~~~~~~~~~~~~~~~~

* html

  * ``lona.html.HTML`` now parses HTML into high level nodes like
    ``lona.html.TextInput``

  * All subclasses of ``lona.html.AbstractNode`` can implement
    ``handle_input_event()`` now

    * Previously only ``lona.html.Widget`` classes could

Changes
~~~~~~~

* html

  * All databinding widgets (``lona.html.TextInput``, ``lona.html.TextArea``,
    ``lona.html.CheckBox`` and ``lona.html.Select``) were ported to nodes

    * Since ``lona.html.AbstractNode`` subclasses can handle their own input
      events there is no need to implement them as widgets anymore

  * ``lona.html.AbstractNode.handle_click()`` and
    ``lona.html.AbstractNode.handle_change()`` for more Javascript like
    callback handling were added

  * ``lona.html.HTML(use_high_level_nodes=True)`` was added to disable
    parsing into high level nodes

  * The Nodes ``lona.html.Html``, ``lona.html.Head`` and ``lona.html.Body``
    were removed

    * There is no way to use them with Lona without breaking HTML5 conventions

Bugfixes
~~~~~~~~

* html

  * Parsing of the ``style`` attribute when using ``lona.html.HTML`` was fixed

    * Previously parsing of HTML nodes that defined a ``style`` attribute
      crashed with a ``ValueError``

  * ``lona.html.TFood`` was renamed to ``lona.html.TFoot``
  * ``lona.html.Fieldset`` had the tag name ``form`` set previously
  * ``lona.html.TextArea`` preserves all whitespaces now when generated by
    using ``lona.html.HTML``


.. changelog-header:: 1.4.1 (2021-08-27)

Changes
~~~~~~~

* html

  * support for defining sub nodes as list was added
  * ``AbstractNode.closest()`` was added

* support for ``python -m lona`` was added


.. changelog-header:: 1.4 (2021-08-26)

Changes
~~~~~~~

* logging

  * the Lona root logger can't be filtered anymore

    * The root logger is used by the command line tools to report errors, for
      example when startup is not possible due an invalid host or port.
      These errors should never be ignored.

  * the default log level was set from ``logging.WARN`` to ``logging.INFO``

* requests

  * ``request.user`` is now writeable

    * In middlewares it makes sense to set ``request.user`` from a
      handle_request hook for authentication or authorization.

  * ``request.interactive`` was added

    * ``request.interactive`` is a shortcut to
      ``request.connection.interactive``

* support for ``NO_COLOR`` environment variable was added

  * more information: `no-color.org <https://no-color.org>`_

Bugfixes
~~~~~~~~

* unique ids in ``lona.html.AbstractNode`` and view runtimes were fixed

  * Previously timestamps generated by ``time.monotonic_ms()`` were used as
    unique ids, but at least on Windows, these timestamps seem not to have an
    high enough resolution.
    This results in HTML trees in which all nodes have the same node id, which
    breaks input events.

* logging

  * ansi colors are now disabled in terminals that don't support them

  * color palette were fixed for light terminals


.. changelog-header:: 1.3 (2021-08-22)

Breaking Changes
~~~~~~~~~~~~~~~~

* html: inputs: ``TextInput``, ``TextArea``, ``CheckBox``, ``Select``:
  ``input_event.node`` now contain the outer widget, not the inner node to
  make checks in views simpler

* sessions: the session middleware now skips cookie setting and redirecting on
  non interactive views to make REST APIs work as expected

Changes
~~~~~~~

* routing: the router now uses ``functools.lru_cache`` for ``resolve()`` and
  ``reverse()``
* html: parsing: obsolete empty ``TextNode`` objects that are not part of a
  ``pre`` get filtered out now
* views: non-interactive views can return Lona HTML trees now

Bugfixes
~~~~~~~~

* views: ``GET`` variables were fixed for non-interactive views
* views: handling of empty return values for non-interactive views like
  ``''`` or ``None`` was fixed


.. changelog-header:: 1.2 (2021-08-19)

Breaking Changes
~~~~~~~~~~~~~~~~

* contrib: contrib.django was moved to `github.com/lona-web-org/lona-django <https://github.com/lona-web-org/lona-django>`_
* contrib: contrib.chartjs was moved to `github.com/lona-web-org/lona-chartjs <https://github.com/lona-web-org/lona-chartjs>`_
* contrib: contrib.bootstrap3 was removed

Changes
~~~~~~~

* frontend: the default frontend was split up in multiple templates, JS and CSS
  files to make it more configurable
* shell: the commands ``%lona_static_files``, ``%lona_templates`` and
  ``%lona_middlewares`` were added

Bugfixes
~~~~~~~~

* scripts: static file loading issues were fixed

  * previously ``app.add_static_file()`` and ``app.add_template()`` couldn't
    override default static files and templates

* shell: ``%lona_views``: python stack analysis when running from a Lona script
  was fixed

* shell: ``%lona_views``: fix error message when using ``--memory``

  * previously ``%lona_views`` would always return "invalid runtime id" when
    ``--memory`` is set.


.. changelog-header:: 1.1.1 (2021-08-15)

Bugfixes
~~~~~~~~

* html: nodes: Button: fix ``disabled`` property


.. changelog-header:: 1.1 (2021-08-13)

Changes
~~~~~~~

* templating: add support for symlinks
* add Lona scripts
* add import shortcuts for ``LonaView``, ``Route``,
  ``ForbiddenError``, ``ClientError``, ``UserAbort`` and ``ServerStop``


.. changelog-header:: 1.0.2 (2021-08-12)

Bugfixes
~~~~~~~~

* command line: collect-static: fix wrong usage of shutil.copy

  * Previously collect-static crashed with a IsADirectoryError when trying to
    copy a directory


.. changelog-header:: 1.0.1 (2021-08-10)

Bugfixes
~~~~~~~~

* html: data binding: skip all non change events

  * Previously ``TextInput`` and ``Select`` catched all input events and
    handled them as ``CHANGE`` event. Now unknown events get bubbled up.


.. changelog-header:: 1.0 (2021-08-09)

Initial stable release
