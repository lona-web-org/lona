def setup_app(app):
    from lona.html import TextInput, FOCUS
    from lona import View

    @app.route('/')
    class MyView(View):
        def handle_request(self, request):
            self.show(TextInput(events=[FOCUS]))
            self.await_focus()
            self.show('SUCCESS')


async def test_focus_events(lona_app_context):
    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url())
        assert await page.inner_text('#lona') != 'SUCCESS'
        await page.focus('input')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')
