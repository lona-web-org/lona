def setup_app(app):
    from lona import View

    # root
    @app.route('/')
    class RootView(View):
        def handle_request(self, request):
            return 'ROOT'

    @app.route('/redirect-to-root/')
    class RedirectToRoot(View):
        def handle_request(self, request):
            return {
                'redirect': '/',
            }

    # absolute url
    @app.route('/absolute-url/')
    class AbsoluteUrlView(View):
        def handle_request(self, request):
            return 'ABSOLUTE-URL'

    @app.route('/redirect-to-absolute-url/')
    class RedirectToAbsoluteUrlView(View):
        def handle_request(self, request):
            return {
                'redirect': '/absolute-url/',
            }

    # relative urls
    @app.route('/redirect-to-relative-url/foo/')
    class RelativeUrlView(View):
        def handle_request(self, request):
            return 'relative-URL'

    @app.route('/redirect-to-relative-url/')
    class RelativeRedirectUrlView(View):
        def handle_request(self, request):
            return {
                'redirect': 'foo/',
            }

    @app.route('/redirect-to-root-relatively/')
    class RedirectToRootRelativeView(View):
        def handle_request(self, request):
            return {
                'redirect': '..',
            }

    # refresh
    refreshed = False

    @app.route('/refresh/')
    class RefreshView(View):
        def handle_request(self, request):
            nonlocal refreshed

            if not refreshed:
                refreshed = True

                return {
                    'redirect': '.',
                }

            else:
                return 'REFRESH'


async def test_redirects(lona_app_context):
    """
    This test tests redirects by creating multiple views and redirecting from
    one to another. Absolute and relative URLs are tested.
    """

    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # test redirect to root
        await page.goto(context.make_url('/redirect-to-root/'))
        await page.wait_for_url('/')
        await page.wait_for_selector('#lona:has-text("ROOT")')

        # test redirect to absolute url
        await page.goto(context.make_url('/redirect-to-absolute-url/'))
        await page.wait_for_url('/absolute-url/')
        await page.wait_for_selector('#lona:has-text("ABSOLUTE-URL")')

        # relative url
        await page.goto(context.make_url('/redirect-to-relative-url/'))
        await page.wait_for_url('/redirect-to-relative-url/foo/')
        await page.wait_for_selector('#lona:has-text("RELATIVE-URL")')

        await page.goto(context.make_url('/redirect-to-root-relatively/'))
        await page.wait_for_url('/')
        await page.wait_for_selector('#lona:has-text("ROOT")')

        # test refresh
        await page.goto(context.make_url('/refresh/'))
        await page.wait_for_url('/refresh/')
        await page.wait_for_selector('#lona:has-text("REFRESH")')
