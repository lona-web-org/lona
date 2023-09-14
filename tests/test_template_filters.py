from lona import TemplateResponse, View


def setup_app(app):
    app.settings.TEMPLATE_EXTRA_FILTERS = {
        'custom_reverse': lambda string: string[::-1],
    }

    app.add_template('template_filters.html', "{{'foo'|custom_reverse}}")

    @app.route('/')
    class TemplateFiltersView(View):
        def handle_request(self, request):
            return TemplateResponse('template_filters.html')


async def test_template_filters(lona_app_context):
    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url('/'))
        await page.wait_for_selector('#lona:has-text("oof")')
