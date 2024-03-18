import pytest


@pytest.mark.parametrize('client_version', [1, 2])
@pytest.mark.parametrize('browser_name', ['chromium', 'firefox', 'webkit'])
async def test_client_history(
        browser_name,
        client_version,
        lona_app_context,
):

    """
    This test checks if the browser history works correctly by navigating
    a browser page using the back and forward "buttons".
    """

    from playwright.async_api import async_playwright

    from lona.html import HTML, H1, A
    from lona import View

    def setup_app(app):

        @app.route('/<title>')
        class TestView(View):
            def handle_request(self, request):
                return HTML(
                    H1(request.match_info['title']),
                    A('foo', href='/foo', _id='foo'),
                    A('bar', href='/bar', _id='bar'),
                    A('baz', href='/baz', _id='baz'),
                )

        @app.route('/')
        class Index(View):
            def handle_request(self, request):
                return HTML(
                    H1('index'),
                    A('foo', href='/foo', _id='foo'),
                    A('bar', href='/bar', _id='bar'),
                    A('baz', href='/baz', _id='baz'),
                )

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # external site, about:blank
        await page.goto('about:blank')
        await page.wait_for_url('about:blank')

        # /
        await page.goto(context.make_url('/'))
        await page.wait_for_url('/')
        await page.wait_for_selector('h1:has-text("index")')

        # /foo
        await page.click('#foo')
        await page.wait_for_url('/foo')
        await page.wait_for_selector('h1:has-text("foo")')

        # /bar
        await page.click('#bar')
        await page.wait_for_url('/bar')
        await page.wait_for_selector('h1:has-text("bar")')

        # back to /foo
        await page.go_back()
        await page.wait_for_url('/foo')
        await page.wait_for_selector('h1:has-text("foo")')

        # forward to /bar
        await page.go_forward()
        await page.wait_for_url('/bar')
        await page.wait_for_selector('h1:has-text("bar")')

        # back to /
        await page.go_back()
        await page.go_back()
        await page.wait_for_url('/')
        await page.wait_for_selector('h1:has-text("index")')

        # back to external site
        await page.go_back()
        await page.wait_for_url('about:blank')

        # forward to /foo
        await page.go_forward()
        await page.go_forward()
        await page.wait_for_url('/foo')
        await page.wait_for_selector('h1:has-text("foo")')
