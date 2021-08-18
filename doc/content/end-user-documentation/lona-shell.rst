

Lona Shell
==========

The Lona shell is based on `rlpython <https://pypi.org/project/rlpython/>`_ and
can be started directly from the server process using ``--shell``, when using
script using ``app.run(shell=True)`` and a shell server and can be embedded
using ``server.embed_shell()`` or ``LonaView.embed_shell()``.

The shell is a full python REPL and contains some use full commands prefixed
with ``%lona_``.

**More information on all Lona shell commands:**
`Lona Shell <end-user-documentation/debugging.html#lona-shell>`_


Analyzing Views
---------------

``%lona_views`` lists all running views, their runtime id, their thread id and
their state.

.. code-block:: text

    >>> %lona_views

    +-----------------+-----------------+-------+-----------------------------------------------+----------+-----------------------+-------------------+
    | Runtime ID      | Thread ID       | Flags | User                                          | Route ID | URL                   | State             |
    +-----------------+-----------------+-------+-----------------------------------------------+----------+-----------------------+-------------------+
    | 190970657505620 | 140228157220608 |       | <AnonymousUser(Fs5Wv4ZA1445TJqgCXKLnMPp9EXZ)> | 26       | /events/click-events/ | WAITING_FOR_INPUT |
    +-----------------+-----------------+-------+-----------------------------------------------+----------+-----------------------+-------------------+

When a valid runtime id is given all internal state of the runtime, the view
and its Python stack are printed.

.. code-block:: text

    >>> %lona_views 190970657505620

    Runtime Info
    ============
    Thread ID: 140228157220608
    Thread Name: LonaRuntimeWorker_1
    View ID: 190970657505620
    Multi user: False
    Daemon: False
    Started at: 2021-08-18 21:02:47.360176
    Stopped at: -
    State: WAITING_FOR_INPUT

    View Info
    =========
    Name: ClickEventView
    Path: /home/fsc/devel/lona/test_project/views/events/click_events.py
    User: <AnonymousUser(Fs5Wv4ZA1445TJqgCXKLnMPp9EXZ)>
    Route: <Route(/events/click-events/, views/events/click_events.py::ClickEventView)>
    Match info: {}
    Method: 'GET'
    GET Data: {}
    POST Data: {}

    Connections
    ===========
                                            User: Connection
    <AnonymousUser(Fs5Wv4ZA1445TJqgCXKLnMPp9EXZ)>: <lona.connection.Connection object at 0x7f89c84f6050>

    Shortened Stack
    ===============
    File "/home/fsc/devel/lona/test_project/views/events/click_events.py", line 61, in handle_request
        input_event = self.await_click(html=html)

When ``--memory`` is set, all variables in ``handle_request()`` are printed.

.. code-block:: text

    >>> %lona_views 191239324037030 --memory

    View Memory
    ===========

    File "/home/fsc/devel/lona/test_project/views/window_actions/set_title.py", line 27, in handle_request
        self.sleep(1)
    +---------+----------------------------------------------------------------------------------------------------------------+
    | Key     | Value                                                                                                          |
    +---------+----------------------------------------------------------------------------------------------------------------+
    | self    | </home/fsc/devel/lona/test_project/views/window_actions/set_title.py.WindowTitleView object at 0x7f89c851a090> |
    | request | <lona.request.Request object at 0x7f89c851a150>                                                                |
    |         |                                                                                                                |
    | div     | <div data-lona-node-id="191239327756320">                                                                      |
    |         |   Using set_title(); Title should be 'Title 2'                                                                 |
    |         | </div>                                                                                                         |
    |         |                                                                                                                |
    | html    | <!--lona-widget:191239327428638-->                                                                             |
    |         | <h2 data-lona-node-id="191239326942719">                                                                       |
    |         |   Set Title                                                                                                    |
    |         | </h2>                                                                                                          |
    |         | <a data-lona-node-id="191239327193636" href="/">                                                               |
    |         |   Back                                                                                                         |
    |         | </a>                                                                                                           |
    |         | <div data-lona-node-id="191239327756320">                                                                      |
    |         |   Using set_title(); Title should be 'Title 2'                                                                 |
    |         | </div>                                                                                                         |
    |         | <!--end-lona-widget:191239327428638-->                                                                         |
    |         |                                                                                                                |
    | i       | 2                                                                                                              |
    | title   | 'Title 2'                                                                                                      |
    +---------+----------------------------------------------------------------------------------------------------------------+


Analyzing Threads
-----------------

``%threads`` lists all running Python threads.

.. code-block:: text

    >>> %threads

    +-----------------+------------------------+-------+--------+-------------------------------------------------------------------------------------------------------+
    | Thread ID       | Thread Name            | Alive | Daemon | Task                                                                                                  |
    +-----------------+------------------------+-------+--------+-------------------------------------------------------------------------------------------------------+
    | 139741524215552 | rlpython REPL Server   | True  | True   | /home/fsc/.pyenv/versions/3.7.9/lib/python3.7/socket.py:212 accept                                    |
    | 139741507430144 | LonaWorker_0           | True  | True   | /home/fsc/.pyenv/versions/3.7.9/lib/python3.7/concurrent/futures/thread.py:78 _worker                 |
    | 139741489948416 | LonaWorker_1           | True  | True   | /home/fsc/.pyenv/versions/3.7.9/lib/python3.7/concurrent/futures/thread.py:78 _worker                 |
    | 139740988831488 | LonaRuntimeWorker_0    | True  | True   | /home/fsc/.pyenv/versions/3.7.9/lib/python3.7/threading.py:296 wait                                   |
    | 139741561206592 | MainThread             | True  | False  | /home/fsc/.pyenv/versions/3.7.9/lib/python3.7/selectors.py:468 select                                 |
    | 139741515822848 | ThreadPoolExecutor-0_0 | True  | True   | /home/fsc/devel/lona/test_project/env/lib/python3.7/site-packages/rlpython/commands/threads.py:85 run |
    | 139741498951424 | ThreadPoolExecutor-0_1 | True  | True   | /home/fsc/.pyenv/versions/3.7.9/lib/python3.7/concurrent/futures/thread.py:78 _worker                 |
    | 139741481555712 | LonaWorker_2           | True  | True   | /home/fsc/.pyenv/versions/3.7.9/lib/python3.7/concurrent/futures/thread.py:78 _worker                 |
    | 139741473163008 | LonaWorker_3           | True  | True   | /home/fsc/.pyenv/versions/3.7.9/lib/python3.7/concurrent/futures/thread.py:78 _worker                 |
    +-----------------+------------------------+-------+--------+-------------------------------------------------------------------------------------------------------+

When a thread id is set, the Python stack of the given thread gets printed.

.. code-block:: text

    >>> %threads 139741561206592

    STACK: MainThread id=139741561206592
      File "/home/fsc/devel/lona/test_project/env/bin/lona", line 7, in <module>
        exec(compile(f.read(), __file__, 'exec'))
      File "/home/fsc/devel/lona/bin/lona", line 8, in <module>
        handle_command_line(sys.argv)
      File "/home/fsc/devel/lona/lona/command_line/handle_command_line.py", line 232, in handle_command_line
        run_server(args)
      File "/home/fsc/devel/lona/lona/command_line/run_server.py", line 106, in run_server
        _run_app()
      File "/home/fsc/devel/lona/lona/command_line/run_server.py", line 76, in _run_app
        shutdown_timeout=args.shutdown_timeout,
      File "/home/fsc/devel/lona/test_project/env/lib/python3.7/site-packages/aiohttp/web.py", line 508, in run_app
        loop.run_until_complete(main_task)
      File "/home/fsc/.pyenv/versions/3.7.9/lib/python3.7/asyncio/base_events.py", line 574, in run_until_complete
        self.run_forever()
      File "/home/fsc/.pyenv/versions/3.7.9/lib/python3.7/asyncio/base_events.py", line 541, in run_forever
        self._run_once()
      File "/home/fsc/.pyenv/versions/3.7.9/lib/python3.7/asyncio/base_events.py", line 1750, in _run_once
        event_list = self._selector.select(timeout)
      File "/home/fsc/.pyenv/versions/3.7.9/lib/python3.7/selectors.py", line 468, in select
        fd_event_list = self._selector.poll(timeout, max_ev)
    END STACK
