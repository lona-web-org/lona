def setup_app(app):
    from lona.html import Button
    from lona import LonaView

    @app.route('/')
    class MyLonaView(LonaView):
        def handle_request(self, request):
            self.show(Button('click me!'))
            self.await_click()
            self.show('SUCCESS')


async def test_rendering(lona_app_context):
    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url())
        assert await page.inner_text('#lona') != 'SUCCESS'
        await page.click('button')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')
