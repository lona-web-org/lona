from playwright.async_api import async_playwright

from lona.html import Button
from lona import LonaView


async def test_rendering(lona_view_context):
    class MyLonaView(LonaView):
        def handle_request(self, request):
            self.show(Button('click me!'))
            self.await_click()
            self.show('SUCCESS')

    context = await lona_view_context(MyLonaView)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url())
        assert await page.inner_text('#lona') != 'SUCCESS'
        await page.click('button')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')
