async def test_simple_daemon_view(lona_app_context):
    """
    This test tests if a the state a daemonized view is hold by the server over
    page refreshes, until the view gets stopped by the user.
    """

    from playwright.async_api import async_playwright

    from lona.pytest import eventually

    def setup_app(app):
        from datetime import datetime

        from lona.html import Button, HTML, Div
        from lona import View

        # TODO: remove in 2.0
        @app.route('/async/')
        class AsyncDaemonView(View):
            def handle_request(self, request):
                self.daemonize()

                message = Div(f'view started: {datetime.now()}', _id='message')

                html = HTML(
                    message,
                    Button('Stop', _id='stop'),
                )

                self.show(html)
                self.await_input_event()
                message.set_text('view stopped')
                self.show(html)

        @app.route('/sync/')
        class SyncDaemonView(View):
            STOP_DAEMON_WHEN_VIEW_FINISHES = False

            def handle_stop_button_click(self, input_event):
                self.is_daemon = False
                self.message.set_text('view stopped')

            def handle_request(self, request):
                self.is_daemon = True

                self.message = Div(
                    f'view started: {datetime.now()}',
                    _id='message',
                )

                return HTML(
                    self.message,
                    Button(
                        'Stop',
                        _id='stop',
                        handle_click=self.handle_stop_button_click,
                    ),
                )

    context = await lona_app_context(setup_app)

    for url in ('/async/', '/sync/'):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            browser_context = await browser.new_context()
            page = await browser_context.new_page()

            # initial load
            await page.goto(context.make_url(url))
            await page.wait_for_selector('#message')
            message1 = await page.inner_text('#message')

            # second load
            await page.goto(context.make_url(url))
            await page.wait_for_selector('#message')
            message2 = await page.inner_text('#message')

            assert message1 == message2

            # stop view
            await page.click('#stop')

            for attempt in eventually():
                async with attempt:
                    message3 = await page.inner_text('#message')

                    assert message3 == 'view stopped'

            # check if views got removed from the server
            await page.goto('about:blank')

            for attempt in eventually():
                async with attempt:
                    view_runtime_count = len(
                        context.server._view_runtime_controller._view_runtimes)

                    assert view_runtime_count == 0


async def test_multi_tab_daemon_view(lona_app_context):
    """
    This test tests the HTML synchronization between two tabs that show same,
    daemonized view, using a TextInput
    """

    from playwright.async_api import async_playwright

    from lona.pytest import eventually

    def setup_app(app):
        from lona.html import TextInput, HTML
        from lona import View

        @app.route('/')
        class DaemonView(View):
            def handle_request(self, request):
                self.daemonize()

                html = HTML(
                    TextInput(value='initial', _id='input'),
                )

                self.show(html)
                self.await_input_event()

    context = await lona_app_context(setup_app)

    async def get_value(page):
        return await page.input_value('#input')

    async def set_value(page, value):
        return await page.fill('#input', str(value))

    async with async_playwright() as p:
        browser1 = await p.chromium.launch()
        browser_context1 = await browser1.new_context()
        page1 = await browser_context1.new_page()
        page2 = await browser_context1.new_page()

        browser2 = await p.chromium.launch()
        browser_context2 = await browser2.new_context()
        page3 = await browser_context2.new_page()

        # initial load
        await page1.goto(context.make_url('/'))
        await page2.goto(context.make_url('/'))
        await page3.goto(context.make_url('/'))

        assert (await get_value(page1)) == 'initial'
        assert (await get_value(page2)) == 'initial'
        assert (await get_value(page3)) == 'initial'

        # set value in first tab
        await set_value(page1, 'foo')

        for attempt in eventually():
            async with attempt:
                assert (await get_value(page1)) == 'foo'
                assert (await get_value(page2)) == 'foo'
                assert (await get_value(page3)) == 'initial'

        # set value in second tab
        await set_value(page2, 'bar')

        for attempt in eventually():
            async with attempt:
                assert (await get_value(page1)) == 'bar'
                assert (await get_value(page2)) == 'bar'
                assert (await get_value(page3)) == 'initial'
