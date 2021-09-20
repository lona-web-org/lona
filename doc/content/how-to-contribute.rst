search_index_weight: -10


How To Contribute
=================

Patches / Issues
----------------

All patches, review and issue-tracking is done on
`Github <http://github.com/lona-web-org/lona>`_.

Tests
-----

To run the test-suite go to ``lona/`` and run ``make test`` or
``make ci-test``.


Linters
-------

To run the linters go to ``lona/`` and run ``make lint``.


Sort Imports
------------

To keep imports consistent run ``make isort`` in repo's root.
It automatically sorts imports in all files.


Test Project
------------

Lona has a test project that uses pretty much any feature Lona has. To start
the test project go to ``lona/test_project`` and run ``make server``.


Documentation
-------------

The documentation is uses `Flamingo <http://flamingo-web.org>`_. To build the
documentation locally go to ``lona/doc`` and run ``make server``. Flamingo
then runs a development server on port ``8080``.
