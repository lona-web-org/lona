from pprint import pformat

from lona.html import Button, HTML, Pre, Div, H2, A
from lona.static_files import Script
from lona.view import View


class CustomEventNode(Div):
    STATIC_FILES = [
        Script(name='CustomEvent', path='custom_event.js'),
    ]

    WIDGET = 'custom_event'

    def __init__(self):
        super().__init__()

        self.pre = Pre(
            '{}',
            style={
                'background-color': 'lightgrey',
            },
        )

        self.nodes = [
            Div(
                Div(
                    Button('None Node Event', _id='non-node-event'),
                    Button('Node Event', _id='node-event'),
                    style={
                        'float': 'left',
                        'width': '50%',
                    },
                ),
                Div(
                    self.pre,
                    style={
                        'float': 'left',
                        'width': '50%',
                    },
                ),
            ),
        ]

    def handle_input_event(self, input_event):
        data = {
            'node': input_event.node.id,
            'type': input_event.type,
            'name': input_event.name,
            'data': input_event.data,
        }

        self.pre.set_text(pformat(data))


class CustomEventView(View):
    def handle_request(self, request):
        html = HTML(
            H2('Custom Event'),
            A('Home', href='/'),
            CustomEventNode(),
        )

        self.show(html)
