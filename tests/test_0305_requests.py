async def test_post_requests(lona_app_context):
    """
    This test checks if <form>-requests as GET and POST work as intended.
    """

    import json

    from playwright.async_api import async_playwright

    from lona.html import TextInput, Submit, HTML, Form, Div
    from lona import View

    def setup_app(app):

        @app.route('/')
        class Index(View):
            def handle_request(self, request):
                return HTML(
                    Div(request.method, _id='method'),
                    Div(json.dumps(request.POST), _id='post-data'),
                    Form(
                        TextInput(name='input-1'),
                        Submit(),
                        method='POST',
                    ),
                )

    context = await lona_app_context(setup_app)

    async def get_method(page):
        element = page.locator('#method')

        return (await element.inner_html())

    async def get_post_data(page):
        element = page.locator('#post-data')
        json_string = await element.inner_html()

        return json.loads(json_string)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # GET request
        await page.goto(context.make_url('/'))
        await page.wait_for_url('/')

        assert await get_method(page) == 'GET'
        assert await get_post_data(page) == {}

        # POST request
        await page.locator('input[name=input-1]').fill('foo')
        await page.click('input[type=submit]')

        await page.wait_for_url('/')

        assert await get_method(page) == 'POST'
        assert await get_post_data(page) == {'input-1': 'foo'}
