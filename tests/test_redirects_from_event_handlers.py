import pytest

from lona import RedirectResponse, View
from lona.html import Button


def get_setup_app_callback(response_format):
    def setup_app(app):
        class RedirectButton(Button):
            def handle_input_event(self, input_event):
                if response_format == 'response-dict':
                    return {
                        'redirect': '/',
                    }

                elif response_format == 'response-class':
                    return RedirectResponse('/')

        @app.route('/')
        class Index(View):
            def handle_request(self, request):
                return 'SUCCESS'

        @app.route('/redirect-from-handle-input-event-root/')
        class RedirectFromHandleInputEventRootView(View):
            def handle_request(self, request):
                return RedirectButton()

            def handle_input_event_root(self, input_event):
                if response_format == 'response-dict':
                    return {
                        'redirect': '/',
                    }

                elif response_format == 'response-class':
                    return RedirectResponse('/')

        @app.route('/redirect-from-handle-input-event/')
        class RedirectFromHandleInputEventView(View):
            def handle_request(self, request):
                return Button()

            def handle_input_event(self, input_event):
                if response_format == 'response-dict':
                    return {
                        'redirect': '/',
                    }

                elif response_format == 'response-class':
                    return RedirectResponse('/')

        @app.route('/redirect-from-button/')
        class RedirectFromButtonView(View):
            def handle_request(self, request):
                return RedirectButton()

        @app.route('/redirect-from-on-view-event/')
        class RedirectFromOnViewEvent(View):
            def handle_request(self, request):
                return 'REDIRECT FROM ON VIEW EVENT'

            def on_view_event(self, view_event):
                if response_format == 'response-dict':
                    return {
                        'redirect': '/',
                    }

                elif response_format == 'response-class':
                    return RedirectResponse('/')

    return setup_app


@pytest.mark.parametrize(
    'response_format', ['response-dict', 'response-class'],
)
async def test_redirects_from_event_handlers(response_format, lona_app_context):
    """
    This test tests redirects from

     - View.handle_input_event_root()
     - View.handle_input_event()
     - View.on_view_event()
    """

    from playwright.async_api import async_playwright

    context = await lona_app_context(get_setup_app_callback(response_format))

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # test redirect from View.handle_input_event_root()
        await page.goto(
            context.make_url('/redirect-from-handle-input-event-root/'),
        )

        await page.wait_for_url('/redirect-from-handle-input-event-root/')

        await page.click('button')

        await page.wait_for_url('/')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')

        # test redirect from View.handle_input_event()
        await page.goto(
            context.make_url('/redirect-from-handle-input-event/'),
        )

        await page.wait_for_url('/redirect-from-handle-input-event/')

        await page.click('button')

        await page.wait_for_url('/')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')

        # test redirect from button
        await page.goto(
            context.make_url('/redirect-from-button/'),
        )

        await page.wait_for_url('/redirect-from-button/')

        await page.click('button')

        await page.wait_for_url('/')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')

        # test redirect from View.on_view_event()
        await page.goto(
            context.make_url('/redirect-from-on-view-event/'),
        )

        await page.wait_for_url('/redirect-from-on-view-event/')
        await page.wait_for_selector('#lona:has-text("REDIRECT FROM ON VIEW EVENT")')

        context.server.fire_view_event('foo')

        await page.wait_for_url('/')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')
