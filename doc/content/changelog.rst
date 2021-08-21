toctree: False


Changelog
=========

`1.2 <https://github.com/lona-web-org/lona/releases/tag/1.2>`_ (2021-08-19)
---------------------------------------------------------------------------

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


`1.1.1 <https://github.com/lona-web-org/lona/releases/tag/1.1.1>`_ (2021-08-15)
-------------------------------------------------------------------------------

Bugfixes
~~~~~~~~

* html: nodes: Button: fix ``disabled`` property


`1.1 <https://github.com/lona-web-org/lona/releases/tag/1.1>`_ (2021-08-13)
---------------------------------------------------------------------------

Changes
~~~~~~~

* templating: add support for symlinks
* add Lona scripts
* add import shortcuts for ``LonaView``, ``Route``,
  ``ForbiddenError``, ``ClientError``, ``UserAbort`` and ``ServerStop``


`1.0.2 <https://github.com/lona-web-org/lona/releases/tag/1.0.2>`_ (2021-08-12)
-------------------------------------------------------------------------------

Bugfixes
~~~~~~~~

* command line: collect-static: fix wrong usage of shutil.copy

  * Previously collect-static crashed with a IsADirectoryError when trying to
    copy a directory


`1.0.1 <https://github.com/lona-web-org/lona/releases/tag/1.0.1>`_ (2021-08-10)
-------------------------------------------------------------------------------

Bugfixes
~~~~~~~~

* html: data binding: skip all non change events

  * Previously ``TextInput`` and ``Select`` catched all input events and
    handled them as ``CHANGE`` event. Now unknown events get bubbled up.

`1.0 <https://github.com/lona-web-org/lona/releases/tag/1.0>`_ (2021-08-09)
---------------------------------------------------------------------------

Initial stable release