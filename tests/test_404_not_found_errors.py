from lona import NotFoundError, View


def setup_app(app):

    @app.error_404_view
    class Error404NotFoundView(View):
        def handle_request(self, request):
            return 'NOT FOUND'

    @app.route('/url/<name>')
    class View2(View):
        def handle_request(self, request):
            if request.match_info['name'] == 'foo':
                raise NotFoundError

            return request.match_info['name']


async def test_404_not_found_errors(lona_app_context):
    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as playwright:
        context.server.state['view1'] = []
        context.server.state['view2'] = []

        browser = await playwright.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url('/foo'))
        await page.wait_for_selector('body:has-text("NOT FOUND")')

        await page.goto(context.make_url('/url/foo'))
        await page.wait_for_selector('#lona:has-text("NOT FOUND")')

        await page.goto(context.make_url('/url/bar'))
        await page.wait_for_selector('#lona:has-text("bar")')
