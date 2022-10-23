from playwright.async_api import async_playwright
import pytest

from lona.html import Select2, Option2
from lona.pytest import eventually
from lona import View

GET_OPTIONS = 'e => Array.from(e.selectedOptions).map(option => option.value)'


@pytest.mark.parametrize('client_version', [1, 2])
@pytest.mark.parametrize('browser_name', ['chromium', 'firefox', 'webkit'])
async def test_selects2(browser_name, client_version, lona_app_context):
    """
    This test tests HTML selects and multi selects, with and without pre
    selections, using a browser.
    """

    test_data = {}

    def setup_app(app):
        app.settings.CLIENT_VERSION = client_version

        # select ##############################################################
        @app.route('/select/nothing-selected/')
        class NothingSelected(View):
            def handle_request(self, request):
                select = Select2(
                    Option2('Foo', value='foo'),
                    Option2('Bar', value='bar'),
                    Option2('Baz', value='baz'),
                    bubble_up=True,
                )

                test_data['select/nothing-selected'] = select.value

                self.show(select)

                self.await_change(select)
                test_data['select/nothing-selected'] = select.value

        @app.route('/select/pre-selected/')
        class PreSelected(View):
            def handle_request(self, request):
                select = Select2(
                    Option2('Foo', value='foo'),
                    Option2('Bar', value='bar', selected=True),
                    Option2('Baz', value='baz'),
                    bubble_up=True,
                )

                test_data['select/pre-selected'] = select.value

                self.show(select)

                self.await_change(select)
                test_data['select/pre-selected'] = select.value

        @app.route('/select/value-types/')
        class ValueTypes(View):
            def handle_request(self, request):
                select = Select2(
                    Option2('Integer', value=1),
                    Option2('Float', value=1.0),
                    Option2('String', value='1'),
                    bubble_up=True,
                )

                test_data['select/value-types'] = select.value

                self.show(select)

                self.await_change(select)
                test_data['select/value-types'] = select.value

        # multi select ########################################################
        @app.route('/multi-select/nothing-selected/')
        class MultiSelectNothingSelected(View):
            def handle_request(self, request):
                select = Select2(
                    Option2('Foo', value='foo'),
                    Option2('Bar', value='bar'),
                    Option2('Baz', value='baz'),
                    multiple=True,
                    bubble_up=True,
                )

                test_data['multi-select/nothing-selected'] = select.value

                self.show(select)

                self.await_change(select)
                test_data['multi-select/nothing-selected'] = select.value

        @app.route('/multi-select/pre-selected/')
        class MultiSelectPreSelected(View):
            def handle_request(self, request):
                select = Select2(
                    Option2('Foo', value='foo', selected=True),
                    Option2('Bar', value='bar', selected=True),
                    Option2('Baz', value='baz'),
                    multiple=True,
                    bubble_up=True,
                )

                test_data['multi-select/pre-selected'] = select.value

                self.show(select)

                self.await_change(select)
                test_data['multi-select/pre-selected'] = select.value

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await getattr(p, browser_name).launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # select / nothing selected ###########################################
        # initial value
        await page.goto(context.make_url('/select/nothing-selected/'))
        await page.wait_for_selector('select')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/nothing-selected'] == 'foo'

        # user select
        await page.select_option('select', 'bar')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['bar']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/nothing-selected'] == 'bar'

        # select / pre selected ###############################################
        # initial value
        await page.goto(context.make_url('/select/pre-selected/'))
        await page.wait_for_selector('select')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['bar']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/pre-selected'] == 'bar'

        # user select
        await page.select_option('select', 'foo')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/pre-selected'] == 'foo'

        # select / value types ################################################
        # integer
        await page.goto(context.make_url('/select/value-types/'))
        await page.wait_for_selector('select')

        await page.select_option('select', label='Integer')
        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['1']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/value-types'] == 1

        # float
        await page.goto(context.make_url('/select/value-types/'))
        await page.wait_for_selector('select')

        await page.select_option('select', label='Float')
        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['1.0']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/value-types'] == 1.0

        # string
        await page.goto(context.make_url('/select/value-types/'))
        await page.wait_for_selector('select')

        await page.select_option('select', label='String')
        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['1']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/value-types'] == '1'

        # multi / nothing selected ############################################
        # initial value
        await page.goto(context.make_url('/multi-select/nothing-selected/'))
        await page.wait_for_selector('select')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == []

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/nothing-selected'] == ()

        # user select
        await page.select_option('select', ['foo', 'bar'])

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo', 'bar']

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/nothing-selected'] == (
                    'foo',
                    'bar',
                )

        # multi / pre selected ################################################
        # initial value
        await page.goto(context.make_url('/multi-select/pre-selected/'))
        await page.wait_for_selector('select')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo', 'bar']

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/pre-selected'] == ('foo', 'bar')

        # user select
        await page.select_option('select', ['foo', 'baz'])

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo', 'baz']

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/pre-selected'] == (
                    'foo',
                    'baz',
                )

        # user deselect
        await page.goto(context.make_url('/multi-select/pre-selected/'))
        await page.wait_for_selector('select')
        await page.select_option('select', [])

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == []

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/pre-selected'] == ()
