

Testing
=======

.. note::

    Testing is officially supported since 1.9

For testing Lona comes with a `pytest <http://docs.pytest.org>`_ plugin, based
on pytest-aiohttp. The plugin contains two fixtures:
`lona_app_context <#lona-app-context-example>`_ and
`lona_project_context <#lona-project-context-example>`_.

`lona_app_context <#lona-app-context-example>`_ spins up a test server using an
API like the
`Lona script interface </end-user-documentation/getting-started.html#running-lona-from-a-script>`_,
`lona_project_context <#lona-project-context-example>`_ takes the project root
and settings of a
`Lona project </end-user-documentation/getting-started.html#starting-a-lona-project-from-the-project-template>`_
to start the test server. Lona test servers run on an unprivileged random port.

The Lona testing infrastructure is meant to be used together with a browser
testing library like `playwright <https://playwright.dev/python/docs/intro>`_
or `selenium <https://selenium-python.readthedocs.io/>`_. The test suite for
the Lona project and all examples in this article use playwright because it is
easy to use and supports asynchronous programming out of the box. If you prefer
selenium, which requires synchronous programming, take a look at
`Writing Synchronous Tests <#writing-synchronous-tests>`_


lona_app_context Example
------------------------

.. code-block:: python

    def setup_app(app):
        from lona.html import Button
        from lona import LonaView

        @app.route('/')
        class MyLonaView(LonaView):
            def handle_request(self, request):
                self.show(Button('click me!'))
                self.await_click()
                self.show('SUCCESS')


    async def test_button_click(lona_app_context):
        from playwright.async_api import async_playwright

        context = await lona_app_context(setup_app)

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            browser_context = await browser.new_context()
            page = await browser_context.new_page()

            await page.goto(context.make_url('/'))
            assert await page.inner_text('#lona') != 'SUCCESS'
            await page.click('button')
            await page.wait_for_selector('#lona:has-text("SUCCESS")')


lona_project_context Example
----------------------------

.. code-block:: python

    async def test_test_project(lona_project_context):
        import os

        from playwright.async_api import async_playwright

        context = await lona_project_context(
            project_root='/home/test-user/my-lona-project,
            settings=['settings.py'],
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            browser_context = await browser.new_context()
            page = await browser_context.new_page()

            await page.goto(context.make_url('/my-url/'))
            await page.wait_for_selector('#lona>h1:has-text("Hello World")')


LonaContext Objects
-------------------

Both `lona_app_context <#lona-app-context-example>`_ and
`lona_project_context <#lona-project-context-example>`_ return an
``lona.pytest.LonaContext`` object that holds all state for the running test.


LonaContext.app
~~~~~~~~~~~~~~~

    Reference to the ``lona.LonaApp`` object of the running test server. When
    using `lona_project_context <#lona-project-context-example>`_ this variable
    is ``None``.


LonaContext.server
~~~~~~~~~~~~~~~~~~

    Reference to the `Server </end-user-documentation/server.html>`_ object of
    the running test server.


LonaContext.loop
~~~~~~~~~~~~~~~~

    Reference to the running asyncio ioloop.


LonaContext.make_url()
~~~~~~~~~~~~~~~~~~~~~~

    .. api-doc:: lona.pytest.LonaContext.make_url


LonaContext.debug_interactive()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. api-doc:: lona.pytest.LonaContext.debug_interactive


Writing Synchronous Tests
-------------------------

If you need to use blocking synchronous code in your test, because you want to
access a database, or your browser testing library does not support
asynchronous code, you can move your actual test code into a thread.

.. code-block:: python

    def setup_app(app):
        from lona.html import HTML, H1
        from lona import LonaView

        @app.route('/my-url/')
        class MyLonaView(LonaView):
            def handle_request(self, request):
                self.my_variable = 'foo'

                return HTML(
                    H1('Hello World'),
                )


    async def test_my_lona_view(lona_app_context, selenium):
        context = await lona_app_context(setup_app)

        # actual test
        def run_test():
            selenium.get(lona_context.make_url('/my-url/'))
            element = selenium.find_element_by_css_selector('h1')

            assert element.text == 'Hello World'

        # run test in a thread
        await context.loop.run_in_executor(None, run_test)


Accessing View Variables From A Test
------------------------------------

To access the variables of a Lona view, you can get your running view object
using
`Server.get_views() </end-user-documentation/server.html#server-get-views>`_.

.. code-block:: python

    def setup_app(app):
        from lona.html import HTML, H1
        from lona import LonaView

        @app.route('/my-url/')
        class MyLonaView(LonaView):
            def handle_request(self, request):
                self.my_variable = 'foo'

                return HTML(
                    H1('Hello World'),
                )


    async def test_my_lona_view(lona_app_context):
        from playwright.async_api import async_playwright

        context = await lona_app_context(setup_app)

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            browser_context = await browser.new_context()
            page = await browser_context.new_page()

            await page.goto(context.make_url())
            await page.wait_for_selector('#lona h1:has-text("Hello World")')

            view = context.server.get_views(url='/my-url/')[0]

            assert view.my_variable == 'foo'


Timing Sensitive Tests
----------------------

Lona has a complex rendering mechanism that has some overhead to it. This means
that some state changes happen slightly delayed, which can result in failing
tests.

``lona.pytest.eventually`` is meant to retry asserts periodically with a
timeout.

    .. api-doc:: lona.pytest.eventually


Tips
----

 * The root HTML element where all Lona views run has the id ``lona`` when
   using the default template. The CSS selector is ``#lona`` in this case.
