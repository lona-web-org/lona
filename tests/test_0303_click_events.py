async def test_click_events(lona_app_context):
    from playwright.async_api import async_playwright

    state = {
        'html': None,
        'input-events': [],
    }

    def setup_app(app):
        from lona.html import CLICK, HTML, Div
        from lona import View

        class OuterDiv(Div):
            EVENTS = [CLICK]

            STYLE = {
                'border': '1px solid black',
                'display': 'inline-flex',
                'background-color': 'lightgrey',
                'flex-direction': 'column',
                'height': '10em',
                'cursor': 'pointer',
                'padding': '1em',
            }

        class InnerDiv(Div):
            EVENTS = [CLICK]

            STYLE = {
                'border': '1px solid black',
            }

        class NonClickableInnerDiv(InnerDiv):
            EVENTS = []

        @app.route('/')
        class ClickTestView(View):
            def handle_input_event(self, input_event):
                state['input-events'].append(input_event)

                self.show('SUCCESS')

            def handle_request(self, request):
                html = HTML(
                    OuterDiv(
                        'Clickable Outer Div 1',
                        InnerDiv(
                            'Clickable Inner Div 1',
                            id='inner-div-1',
                        ),
                        id='outer-div-1',
                    ),
                    OuterDiv(
                        'Clickable Outer Div 2',
                        NonClickableInnerDiv(
                            'Non Clickable Inner Div 2',
                            id='inner-div-2',
                        ),
                        id='outer-div-2',
                    ),
                )

                self.show(html)
                state['html'] = html

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # clickable outer div
        state['input-events'].clear()

        await page.goto(context.make_url())
        assert await page.inner_text('#lona') != 'SUCCESS'
        await page.click('#outer-div-1')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')

        outer_div = state['html'].query_selector('#outer-div-1')
        input_events = state['input-events']

        assert len(input_events) == 1
        assert input_events[0].node is outer_div
        assert input_events[0].target_node is outer_div

        # clickable inner div in clickable div
        state['input-events'].clear()

        await page.goto(context.make_url())
        assert await page.inner_text('#lona') != 'SUCCESS'
        await page.click('#inner-div-1')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')

        inner_div = state['html'].query_selector('#inner-div-1')
        input_events = state['input-events']

        assert len(input_events) == 1
        assert input_events[0].node is inner_div
        assert input_events[0].target_node is inner_div

        # non clickable inner div in clickable div
        state['input-events'].clear()

        await page.goto(context.make_url())
        assert await page.inner_text('#lona') != 'SUCCESS'
        await page.click('#inner-div-2')
        await page.wait_for_selector('#lona:has-text("SUCCESS")')

        outer_div = state['html'].query_selector('#outer-div-2')
        inner_div = state['html'].query_selector('#inner-div-2')
        input_events = state['input-events']

        assert len(input_events) == 1
        assert input_events[0].node is outer_div
        assert input_events[0].target_node is inner_div
