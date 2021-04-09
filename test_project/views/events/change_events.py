from pprint import pformat

from lona.html import TextInputNode, CheckboxNode, Div, H1, Pre, CHANGE
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
            H1('Change Events'),
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

        request.client.show(html)

        while True:
            input_event = request.client.await_change(html=html)

            pre.set_text(
                'changed node: {}\nvalue: {}'.format(
                    input_event.node._id,
                    pformat(input_event.data),
                )
            )
