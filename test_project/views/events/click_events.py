from pprint import pformat

from lona.html import Div, H1, Pre
from lona.view import LonaView
from lona.events import CLICK


class ClickEventView(LonaView):
    def handle_request(self, request):
        colors = ['navy', 'maroon', 'green', 'teal', 'grey', 'purple', 'aqua']

        style = {
            'float': 'left',
            'margin': '3px',
            'width': '50px',
            'height': '50px',
            'cursor': 'pointer',
            'background-color': colors[0],
        }

        pre = Pre(
            '{}',
            style={
                'background-color': 'lightgrey',
            },
        )

        html = Div(
            H1('Click Events'),
            Div(
                Div(
                    Div(style=style, events=[CLICK]),
                    Div(style=style, events=[CLICK]),
                    Div(style=style, events=[CLICK]),
                    Div(style=style, events=[CLICK]),
                    Div(style=style, events=[CLICK]),

                    style={
                        'float': 'left',
                        'width': '50%',
                    },
                ),
                Div(
                    pre,

                    style={
                        'float': 'left',
                        'width': '50%',
                    },
                ),
            ),
        )

        while True:
            input_event = request.client.await_click(html=html)

            data = {
                'node': input_event.node._id,
                'event_data': input_event.data

            }

            pre.set_text(pformat(data))

            next_color = colors[
                colors.index(input_event.node.style['background-color'])-1]

            input_event.node.style['background-color'] = next_color
