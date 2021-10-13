from aiohttp.web import Response


def setup_app(app):
    @app.route('/', http_pass_through=True)
    async def on_view_event(request):
        return Response(
            text='<h1>HTTP PASS THROUGH</h1>',
            content_type='text/html',
        )


async def test_http_pass_through(lona_app_context):
    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url())

        await page.wait_for_selector('h1:has-text("HTTP PASS THROUGH")')
