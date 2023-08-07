def setup_app(app):
    from lona.html import TextInput, Submit, HTML, Form, Div
    from lona import View

    @app.route('/')
    class Index(View):
        def handle_request(self, request):
            extras = []
            if request.method == 'POST':
                extras.append(Div(f'POST: {request.POST["txt"]}', _id='res'))

            return HTML(
                *extras,
                Form(
                    TextInput(name='txt', _id='box'),
                    Submit('Submit'),
                    action='.',
                    method='POST',
                ),
            )


async def test_html_form(lona_app_context):
    """
    This test checks if <form>-requests as GET and POST work as intended.
    """

    from playwright.async_api import async_playwright

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        text = 'SomeTextHere'

        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # Fill in form
        await page.goto(
            context.make_url('/'),
        )
        await page.wait_for_url('/')
        await page.locator('#box').fill(text)
        await page.get_by_text('Submit').press('Enter')

        # Check result
        await page.wait_for_timeout(1000)
        assert await page.locator('#res').text_content() == f'POST: {text}'
