import os.path

from playwright.async_api import async_playwright

from lona.static_files import StyleSheet, Script
from lona import View


def setup_app(app):
    some_existing_file = os.path.basename(__file__)

    @app.route('/')
    class MyView(View):
        STATIC_FILES = [
            StyleSheet(
                name='my-view-style',
                path=some_existing_file,
                url='view.css',
            ),
            Script(
                name='my-view-script',
                path=some_existing_file,
                url='view.js',
            ),
            Script(
                name='my-view-map',
                path=some_existing_file,
                url='view.map',
                link=False,
            ),
            StyleSheet(
                name='my-view-disabled',
                path=some_existing_file,
                url='view.disabled',
                enabled_by_default=False,
            ),
        ]

        def handle_request(self, request):
            return 'SUCCESS'


async def test_static_files_view(lona_app_context):
    context = await lona_app_context(setup_app)

    assert (await context.client.get('/static/view.css')).status == 200
    assert (await context.client.get('/static/view.js')).status == 200
    assert (await context.client.get('/static/view.map')).status == 200
    assert (await context.client.get('/static/view.disabled')).status == 404

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url())
        await page.wait_for_selector('#lona:has-text("SUCCESS")')

        links = await page.query_selector_all('link')
        scripts = await page.query_selector_all('script')
        style_urls = [await x.get_attribute('href') for x in links]
        script_urls = [await x.get_attribute('src') for x in scripts]
        html = await page.inner_html('html')

        assert '/static/view.css' in style_urls
        assert '/static/view.js' in script_urls
        assert 'view.map' not in html
        assert 'view.disabled' not in html
