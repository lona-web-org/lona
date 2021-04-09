from lona.html import HTML, Div, H1, Br, Widget, A
from lona.static_files import Script
from lona.view import LonaView
from lona.json import dumps


class TestWidget(Widget):
    STATIC_FILES = [
        Script(name='TestWidget', path='widget_data.js'),
    ]

    FRONTEND_WIDGET_CLASS = 'widget_data'

    def __init__(self):
        self.server_state = Div()

        self.nodes = [
            self.server_state,
            Div(_id='client-state'),
        ]

    def update_state(self):
        self.server_state.set_text(dumps(self.data))


class WidgetDataView(LonaView):
    def handle_request(self, request):
        widget = TestWidget()

        html = HTML(
            H1('Widget Data'),
            A('Home', href='/'),
            Br(),
            Br(),
            'This view tests the encoding and decoding of abstract widget data.',  # NOQA
            Br(),
            Br(),
            'The first value is the state the server has, the second is the '
            'second is the client state.',
            Br(),
            'Both values should be equal at all times.',
            Br(),
            Br(),
            widget,
        )

        request.client.show(html)

        while True:
            # list
            widget.data = {'list': []}

            for i in range(6):
                widget.data['list'].append(i)
                widget.update_state()
                request.client.show(html)
                request.view.sleep(1)

            widget.data['list'].remove(2)
            widget.update_state()
            request.client.show(html)
            request.view.sleep(1)

            widget.data['list'].insert(2, 2)
            widget.update_state()
            request.client.show(html)
            request.view.sleep(1)

            widget.data['list'].clear()
            widget.update_state()
            request.client.show(html)
            request.view.sleep(1)

            widget.data['list'] = [5, 4, 3, 2, 1]
            widget.update_state()
            request.client.show(html)
            request.view.sleep(1)

            # dict
            widget.data = [{}]

            for i in range(6):
                widget.data[0][i] = i
                widget.update_state()
                request.client.show(html)
                request.view.sleep(1)

            widget.data[0].pop(2)
            widget.update_state()
            request.client.show(html)
            request.view.sleep(1)

            widget.data[0].clear()
            widget.update_state()
            request.client.show(html)
            request.view.sleep(1)

            widget.data[0] = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
            widget.update_state()
            request.client.show(html)
            request.view.sleep(1)
