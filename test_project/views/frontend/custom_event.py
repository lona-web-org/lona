from pprint import pformat

from lona.html import HTML, Div, H1, Widget, Button, Pre, A
from lona.static_files import Script


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
            'node': input_event.node,
            'node_info': input_event.node_info,
            'type': input_event.type,
            'name': input_event.name,
            'data': input_event.data,
        }

        self.pre.set_text(pformat(data))


def handle_request(request):
    widget = CustomEventWidget()

    html = HTML(
        H1('Custom Event'),
        A('Home', href='/'),
        widget,
    )

    request.client.show(html)
