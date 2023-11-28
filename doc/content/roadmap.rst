

Roadmap
=======


Getting Feature Complete
------------------------

- [ ] HTML

  - [ ] Add missing inputs

    - [x] Add radio buttons and radio groups

    - [ ] Add date inputs

      - Support for Year, Week, Local Time, etc

    - [ ] Add password input
    - [ ] Add email input
    - [ ] Add range input
    - [ ] Add color input

- [x] Add support for file uploads
- [ ] Add support for JavaScript Modules


Lona 2.0
--------

- [ ] Names and Imports

  - [ ] Remove ``lona.LonaApp``
  - [ ] Remove ``lona.LonaView``

- [ ] HTML

  - [ ] Remove ``lona.html.Select`` and ``lona.html.Select2``

    - [ ] Rename ``lona.html.Select2`` to ``lona.html.Select``
    - [ ] Rename ``lona.html.Option2`` to ``lona.html.Option``

  - [ ] Remove support for HTML string parsing from ``lona.html.HTML2``

  - [ ] Remove ``lona.html.HTML``

    - [ ] Rename ``lona.html.HTML2`` to ``lona.html.HTML``

  - [ ] Remove ``lona.html.Widget``
  - [ ] Remove ``lona.html.Datalist``
  - [ ] Remove ``lona.html.Fieldset``
  - [ ] Remove ``settings.USE_FUTURE_NODE_CLASSES``

- [ ] Rendering

    - [ ] Remove old JavaScript client

      - [ ] Remove ``client`` and rename ``client2`` to ``client``
      - [ ] Remove ``settings.CLIENT_VERSION``

    - [ ] Remove support for ``lona.html.Widget``

    - [ ] Remove widget hooks ``setup``, ``deconstruct``, ``data_updated``
    - [ ] Remove widget attributes ``nodes`` and ``root_node``

- [ ] Remove support for dict responses

- [ ] Remove old daemon behavior

  - [ ] Remove ``View.daemonize``
  - [ ] Remove ``settings.STOP_DAEMON_WHEN_VIEW_FINISHES``
