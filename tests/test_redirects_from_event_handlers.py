from lona.html import Button
from lona import LonaView


def setup_app(app):
    class RedirectButton(Button):
        def handle_input_event(self, input_event):
            return {
                'redirect': '/',
            }

    @app.route('/redirect-from-handle-input-event-root/')
    class RedirectFromHandleInputEventRootView(LonaView):
        def handle_input_event_root(self, input_event):
            return {
                'redirect': '/',
            }

    @app.route('/redirect-from-handle-input-event/')
    class RedirectFromHandleInputEventView(LonaView):
        def handle_input_event(self, input_event):
            return {
                'redirect': '/',
            }

    @app.route('/redirect-from-button/')
    class RedirectFromButtonView(LonaView):
        def handle_request(self, request):
            return RedirectButton()

    @app.route('/redirect-from-on-view-event/')
    class RedirectFromOnViewEvent(LonaView):
        def on_view_event(self, view_event):
            return {
                'redirect': '/',
            }


async def test_redirects_from_event_handlers(lona_app_context):
    """
    This test tests redirects from

     - LonaView.handle_input_event_root()
     - LonaView.handle_input_event()
     - LonaView.on_view_event()
    """

    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # test redirect from LonaView.handle_input_event_root()
        await page.goto(
            context.make_url('/redirect-from-handle-input-event-root/'),
        )

        await page.wait_for_url('/redirect-from-handle-input-event-root/')
        await page.wait_for_url('/')

        # test redirect from LonaView.handle_input_event()
        await page.goto(
            context.make_url('/redirect-from-handle-input-event/'),
        )

        await page.wait_for_url('/redirect-from-handle-input-event/')
        await page.wait_for_url('/')

        # test redirect from button
        await page.goto(
            context.make_url('/redirect-from-button/'),
        )

        await page.wait_for_url('/redirect-from-button/')

        await page.click('button')

        await page.wait_for_url('/')

        # test redirect from LonaView.on_view_event()
        await page.goto(
            context.make_url('/redirect-from-on-view-event/'),
        )

        await page.wait_for_url('/redirect-from-on-view-event/')

        context.server.fire_view_event('foo')

        await page.wait_for_url('/')
