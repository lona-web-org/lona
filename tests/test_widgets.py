import json

from playwright.async_api import async_playwright

from lona.html import Button, HTML, Div
from lona.static_files import Script
from lona.pytest import eventually
from lona._json import dumps
from lona import View


async def test_widgets(lona_app_context):
    state = {
        'test-node': None,
        'done': False,
    }

    def setup_app(app):

        class TestNode(Div):
            ID_LIST = ['test-node']

            STATIC_FILES = [
                Script(
                    name='test-widget',
                    path='static/test-widget.js',
                ),
            ]

            WIDGET = 'test-widget'

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.widget_data = {}

        @app.route('/')
        class TestView(View):
            def handle_request(self, request):
                test_node = TestNode()

                html = HTML(
                    test_node,
                    Button('Update', _id='update'),
                )

                state['test-node'] = test_node

                # list
                test_node.widget_data = {'list': []}

                for i in range(6):
                    test_node.widget_data['list'].append(i)
                    self.await_input_event(html=html)

                test_node.widget_data['list'].remove(2)
                self.await_input_event(html=html)

                test_node.widget_data['list'].insert(2, 2)
                self.await_input_event(html=html)

                test_node.widget_data['list'].clear()
                self.await_input_event(html=html)

                test_node.widget_data['list'] = [5, 4, 3, 2, 1]
                self.await_input_event(html=html)

                # dict
                test_node.widget_data = [{}]

                for i in range(6):
                    test_node.widget_data[0][i] = i
                    self.await_input_event(html=html)

                test_node.widget_data[0].pop(2)
                self.await_input_event(html=html)

                test_node.widget_data[0].clear()
                self.await_input_event(html=html)

                test_node.widget_data[0] = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
                self.await_input_event(html=html)

                # done
                state['done'] = True

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        await page.goto(context.make_url())

        async def run_test():
            for _ in range(100):
                for attempt in eventually():
                    async with attempt:

                        # check if view is done
                        if state['done']:
                            return

                        # server side widget data
                        server_side_widget_data = json.loads(
                            dumps(state['test-node'].widget_data),
                        )

                        # client side widget data
                        node = await page.query_selector('#test-node')
                        inner_html = await node.inner_html()

                        client_side_widget_data = json.loads(inner_html)

                        # check
                        assert (server_side_widget_data ==
                                client_side_widget_data)

                await page.click('#update')

        await run_test()
