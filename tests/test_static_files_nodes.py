import os.path

from playwright.async_api import async_playwright

from lona.static_files import StyleSheet, Script
from lona.html import Div
from lona import View


def setup_app(app):
    some_existing_file = os.path.basename(__file__)

    class MyNode(Div):
        STATIC_FILES = [
            StyleSheet(
                name='my-node-style',
                path=some_existing_file,
                url='node.css',
            ),
            Script(
                name='my-node-script',
                path=some_existing_file,
                url='node.js',
            ),
            Script(
                name='my-node-map',
                path=some_existing_file,
                url='node.map',
                link=False,
            ),
            StyleSheet(
                name='disabled-node',
                path=some_existing_file,
                url='node.disabled',
                enabled_by_default=False,
            ),
        ]

    @app.route('/')
    class MyView(View):
        def handle_request(self, request):
            return 'SUCCESS'


async def test_static_files_nodes(lona_app_context):
    context = await lona_app_context(setup_app)

    assert (await context.client.get('/static/node.css')).status == 200
    assert (await context.client.get('/static/node.js')).status == 200
    assert (await context.client.get('/static/node.map')).status == 200
    assert (await context.client.get('/static/node.disabled')).status == 404

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

        assert '/static/node.css' in style_urls
        assert '/static/node.js' in script_urls
        assert 'node.map' not in html
        assert 'node.disabled' not in html
