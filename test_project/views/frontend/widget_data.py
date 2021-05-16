from lona.html import HTML, Div, H2, Br, Widget, Select, Strong
from lona.static_files import Script
from lona.view import LonaView
from lona._json import dumps


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

        interval = Select(
            values=[
                (1,    '1s',    False),
                (0.5,  '0.5s',  True),
                (0.25, '0.25s', False),
                (0.01, '0.01s', False),
            ],
        )

        html = HTML(
            H2('Widget Data'),
            'This view tests the encoding and decoding of abstract widget data.',  # NOQA
            Br(),
            Br(),
            'The first value is the state the server has, the second is the '
            'second is the client state.',
            Br(),
            'Both values should be equal at all times.',
            Br(),
            Br(),

            Strong('Interval: '),
            interval,
            Br(),
            Br(),

            widget,
        )

        self.show(html)

        while True:
            # list
            widget.data = {'list': []}

            for i in range(6):
                widget.data['list'].append(i)
                widget.update_state()
                self.show(html)
                self.sleep(float(interval.value))

            widget.data['list'].remove(2)
            widget.update_state()
            self.show(html)
            self.sleep(float(interval.value))

            widget.data['list'].insert(2, 2)
            widget.update_state()
            self.show(html)
            self.sleep(float(interval.value))

            widget.data['list'].clear()
            widget.update_state()
            self.show(html)
            self.sleep(float(interval.value))

            widget.data['list'] = [5, 4, 3, 2, 1]
            widget.update_state()
            self.show(html)
            self.sleep(float(interval.value))

            # dict
            widget.data = [{}]

            for i in range(6):
                widget.data[0][i] = i
                widget.update_state()
                self.show(html)
                self.sleep(float(interval.value))

            widget.data[0].pop(2)
            widget.update_state()
            self.show(html)
            self.sleep(float(interval.value))

            widget.data[0].clear()
            widget.update_state()
            self.show(html)
            self.sleep(float(interval.value))

            widget.data[0] = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
            widget.update_state()
            self.show(html)
            self.sleep(float(interval.value))
