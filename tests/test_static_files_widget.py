import os.path

from playwright.async_api import async_playwright

from lona.static_files import StyleSheet, Script
from lona.html import Widget
from lona import LonaView


async def test_static_files_widget(lona_view_context):
    some_existing_file = os.path.basename(__file__)

    class MyWidget(Widget):
        STATIC_FILES = [
            StyleSheet(
                name='my-widget-style',
                path=some_existing_file,
                url='widget.css',
            ),
            Script(
                name='my-widget-script',
                path=some_existing_file,
                url='widget.js',
            ),
            Script(
                name='my-widget-map',
                path=some_existing_file,
                url='widget.map',
                link=False,
            ),
            StyleSheet(
                name='disabled-widget',
                path=some_existing_file,
                url='widget.disabled',
                enabled_by_default=False,
            ),
        ]

    class MyLonaView(LonaView):
        def handle_request(self, request):
            return 'SUCCESS'

    context = await lona_view_context(MyLonaView)

    assert (await context.client.get('/static/widget.css')).status == 200
    assert (await context.client.get('/static/widget.js')).status == 200
    assert (await context.client.get('/static/widget.map')).status == 200
    assert (await context.client.get('/static/widget.disabled')).status == 404

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

        assert '/static/widget.css' in style_urls
        assert '/static/widget.js' in script_urls
        assert 'widget.map' not in html
        assert 'widget.disabled' not in html
