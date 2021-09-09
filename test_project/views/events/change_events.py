from pprint import pformat

from lona.html import TextInput, CheckBox, Pre, Div, H2
from lona.view import LonaView


class ChangeEventsView(LonaView):
    def handle_request(self, request):
        pre = Pre(
            'nothing changed',
            style={
                'background-color': 'lightgrey',
            },
        )

        html = Div(
            H2('Change Events'),
            Div(
                Div(
                    Div(CheckBox(input_delay=0, bubble_up=True)),
                    Div(
                        TextInput(
                            value='Change me',
                            input_delay=0,
                            bubble_up=True,
                        ),
                    ),
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
                f'changed node: {input_event.node._id}\nvalue: {pformat(input_event.data)}',  # NOQA: E501
            )
