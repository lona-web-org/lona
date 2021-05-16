from pprint import pformat

from lona.html import TextInputNode, CheckboxNode, Div, H2, Pre
from lona.events import CHANGE
from lona.view import LonaView


class ChangeEventsView(LonaView):
    def handle_request(self, request):
        pre = Pre(
            'nothing changed',
            style={
                'background-color': 'lightgrey',
            }
        )

        html = Div(
            H2('Change Events'),
            Div(
                Div(
                    Div(CheckboxNode(events=[CHANGE])),
                    Div(TextInputNode(value='Change me', events=[CHANGE])),
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

        self.show(html)

        while True:
            input_event = self.await_change(html=html)

            pre.set_text(
                'changed node: {}\nvalue: {}'.format(
                    input_event.node._id,
                    pformat(input_event.data),
                )
            )
