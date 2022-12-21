from lona.exceptions import UserAbort
from lona.pytest import eventually
from lona.html import Button
from lona import View


def setup_app(app):

    @app.route('/')
    class HomeView(View):
        def handle_request(self, request):
            return 'HOME'

    @app.route('/test-view/')
    class TestView(View):
        def handle_request(self, request):
            self.show(Button())
            self.await_click()

            self.server.state['hooks'].append('handle_request')

        def on_stop(self, reason):
            self.server.state['hooks'].append('on_stop')
            self.server.state['stop_reason'] = reason

        def on_cleanup(self):
            self.server.state['hooks'].append('on_cleanup')


async def test_view_stop_hooks(lona_app_context):
    """
    This test tests the view hooks on_stop and on_cleanup
    """

    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch()
        browser_context = await browser.new_context()

        # go to page and stop it by clicking the button
        page1 = await browser_context.new_page()

        context.server.state['hooks'] = []
        context.server.state['stop_reason'] = 'NOTSET'

        await page1.goto(context.make_url('/test-view/'))
        await page1.wait_for_selector('button')

        for attempt in eventually():
            async with attempt:
                assert sorted(context.server.state['hooks']) == []
                assert context.server.state['stop_reason'] == 'NOTSET'

        # trigger stop
        await page1.click('button')

        for attempt in eventually():
            async with attempt:
                assert sorted(context.server.state['hooks']) == sorted([
                    'handle_request',
                    'on_stop',
                ])

                assert context.server.state['stop_reason'] is None

        # trigger cleanup
        await page1.goto(context.make_url('/'))
        await page1.wait_for_selector('#lona:has-text("HOME")')

        for attempt in eventually():
            async with attempt:
                assert sorted(context.server.state['hooks']) == sorted([
                    'handle_request',
                    'on_stop',
                    'on_cleanup',
                ])

        # go to page and stop it by reloading the page
        page2 = await browser_context.new_page()

        context.server.state['hooks'] = []
        context.server.state['stop_reason'] = 'NOTSET'

        await page2.goto(context.make_url('/test-view/'))
        await page2.wait_for_selector('button')

        for attempt in eventually():
            async with attempt:
                assert list(context.server.state['hooks']) == []
                assert context.server.state['stop_reason'] == 'NOTSET'

        await page2.reload()
        await page2.wait_for_selector('button')

        for attempt in eventually():
            async with attempt:
                assert sorted(context.server.state['hooks']) == sorted([
                    'on_stop',
                    'on_cleanup',
                ])

                assert isinstance(
                    context.server.state['stop_reason'],
                    UserAbort,
                )
