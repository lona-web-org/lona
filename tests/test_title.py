def setup_app(app):
    from datetime import datetime

    from lona import View

    @app.route('/')
    class HoweView(View):
        def handle_request(self, request):
            return 'HOME'

    @app.route('/daemonized-view/')
    class DaemonizedView(View):
        def handle_request(self, request):
            self.daemonize()
            self.set_title('Daemonized View')
            self.show(f'View started: {datetime.now()}')

            self.await_input_event()


async def test_title(lona_app_context):
    """
    This test tests page titles on non-daemon views and daemon views
    """

    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # test default title
        await page.goto(context.make_url('/'))
        await page.wait_for_selector('#lona:has-text("HOME")')
        assert await page.title() == 'Lona'

        # get timestamp of the daemonized view
        await page.goto(context.make_url('/daemonized-view/'))
        await page.wait_for_selector('#lona:has-text("View started: ")')
        timestamp = await page.inner_text('#lona')

        # test titles
        assert await page.title() == 'Daemonized View'

        # reload tab
        await page.reload()
        await page.wait_for_selector('#lona:has-text("View started: ")')

        assert await page.inner_text('#lona') == timestamp
        assert await page.title() == 'Daemonized View'
