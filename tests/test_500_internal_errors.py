from lona import View


def setup_app(app):

    @app.error_500_view
    class Error500InternalErrorView(View):
        def handle_request(self, request):
            return 'INTERNAL ERROR'

    @app.route('/url/<name>')
    class View2(View):
        def handle_request(self, request):
            if request.match_info['name'] == 'foo':
                raise RuntimeError

            return request.match_info['name']


async def test_500_internal_errors(lona_app_context):
    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as playwright:
        context.server.state['view1'] = []
        context.server.state['view2'] = []

        browser = await playwright.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url('/url/foo'))
        await page.wait_for_selector('#lona:has-text("INTERNAL ERROR")')

        await page.goto(context.make_url('/url/bar'))
        await page.wait_for_selector('#lona:has-text("bar")')
