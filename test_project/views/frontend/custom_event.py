from pprint import pformat

from lona.html import Widget, Button, Pre, Div, A, HTML, H2
from lona.static_files import Script
from lona.view import LonaView


class CustomEventWidget(Widget):
    STATIC_FILES = [
        Script(name='CustomEvent', path='custom_event.js'),
    ]

    FRONTEND_WIDGET_CLASS = 'custom_event'

    def __init__(self):
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


class CustomEventView(LonaView):
    def handle_request(self, request):
        widget = CustomEventWidget()

        html = HTML(
            H2('Custom Event'),
            A('Home', href='/'),
            widget,
        )

        self.show(html)
