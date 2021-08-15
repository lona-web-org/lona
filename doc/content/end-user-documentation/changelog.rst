toctree: False


Changelog
=========

`1.1.1 <https://github.com/lona-web-org/lona/releases/tag/1.1.1>`_
------------------------------------------------------------------

Bugfixes
~~~~~~~~

* html: nodes: Button: fix ``disabled`` property


`1.1 <https://github.com/lona-web-org/lona/releases/tag/1.1>`_
--------------------------------------------------------------

Changes
~~~~~~~

* templating: add support for symlinks
* add Lona scripts
* add import shortcuts for ``LonaView``, ``Route``,
  ``ForbiddenError``, ``ClientError``, ``UserAbort`` and ``ServerStop``


`1.0.2 <https://github.com/lona-web-org/lona/releases/tag/1.0.2>`_
------------------------------------------------------------------

Bugfixes
~~~~~~~~

* command line: collect-static: fix wrong usage of shutil.copy

  * Previously collect-static crashed with a IsADirectoryError when trying to
    copy a directory


`1.0.1 <https://github.com/lona-web-org/lona/releases/tag/1.0.1>`_
------------------------------------------------------------------

Bugfixes
~~~~~~~~

* html: data binding: skip all non change events

  * Previously ``TextInput`` and ``Select`` catched all input events and
    handled them as ``CHANGE`` event. Now unknown events get bubbled up.

`1.0 <https://github.com/lona-web-org/lona/releases/tag/1.0>`_
--------------------------------------------------------------

Initial stable release