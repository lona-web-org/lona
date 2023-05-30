from playwright.async_api import async_playwright

from lona.html import NumberInput, Select, HTML
from lona.pytest import eventually
from lona import View


async def test_number_inputs(lona_app_context):
    test_data = {}

    def setup_app(app):

        @app.route('/')
        class NumberInputView(View):
            def handle_number_input_change(self, input_event):
                number_input = input_event.node

                test_data['valid'] = number_input.valid
                test_data['value'] = number_input.value
                test_data['raw_value'] = number_input.raw_value

            def handle_request(self, request):
                kwargs = {}

                for arg_name in ('min', 'max', 'step'):
                    if arg_name in request.GET:
                        kwargs[arg_name] = int(request.GET[arg_name])

                return HTML(
                    NumberInput(
                        handle_change=self.handle_number_input_change,
                        **kwargs,
                    ),
                    Select(),
                )

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # general tests #######################################################
        await page.goto(context.make_url('/'))
        await page.wait_for_selector('input[type=number]')

        test_data.clear()
        await page.fill('input[type=number]', '10')

        for attempt in eventually():
            async with attempt:
                assert test_data['valid'] is True
                assert test_data['value'] == 10
                assert test_data['raw_value'] == '10'

        # min #################################################################
        await page.goto(context.make_url('/?min=10'))
        await page.wait_for_selector('input[type=number]')

        test_data.clear()
        await page.fill('input[type=number]', '10')

        for attempt in eventually():
            async with attempt:
                assert test_data['valid'] is True
                assert test_data['value'] == 10
                assert test_data['raw_value'] == '10'

        test_data.clear()
        await page.fill('input[type=number]', '3')

        for attempt in eventually():
            async with attempt:
                assert test_data['valid'] is False
                assert test_data['value'] == 3
                assert test_data['raw_value'] == '3'

        # max #################################################################
        await page.goto(context.make_url('/?max=10'))
        await page.wait_for_selector('input[type=number]')

        test_data.clear()
        await page.fill('input[type=number]', '3')

        for attempt in eventually():
            async with attempt:
                assert test_data['valid'] is True
                assert test_data['value'] == 3
                assert test_data['raw_value'] == '3'

        test_data.clear()
        await page.fill('input[type=number]', '11')

        for attempt in eventually():
            async with attempt:
                assert test_data['valid'] is False
                assert test_data['value'] == 11
                assert test_data['raw_value'] == '11'

        # step ################################################################
        await page.goto(context.make_url('/?step=5'))
        await page.wait_for_selector('input[type=number]')

        test_data.clear()
        await page.fill('input[type=number]', '5')

        for attempt in eventually():
            async with attempt:
                assert test_data['valid'] is True
                assert test_data['value'] == 5
                assert test_data['raw_value'] == '5'

        test_data.clear()
        await page.fill('input[type=number]', '10')

        for attempt in eventually():
            async with attempt:
                assert test_data['valid'] is True
                assert test_data['value'] == 10
                assert test_data['raw_value'] == '10'

        test_data.clear()
        await page.fill('input[type=number]', '11')

        for attempt in eventually():
            async with attempt:
                assert test_data['valid'] is False
                assert test_data['value'] == 11
                assert test_data['raw_value'] == '11'
