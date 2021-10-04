toctree: False
search_index_weight: -10


Changelog
=========

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