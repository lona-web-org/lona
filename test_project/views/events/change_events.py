from pprint import pformat

from lona.html import (
    RadioButtonGroup,
    RadioButton,
    TextInput,
    CheckBox,
    Label,
    Pre,
    Div,
    H2,
)
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

                    Div(
                        RadioButtonGroup(
                            Div(
                                Label('Foo', _for='radio-button'),
                                RadioButton(name='radio-button', value='foo'),
                            ),
                            Div(
                                Label('Bar', _for='radio-button'),
                                RadioButton(name='radio-button', value='bar'),
                            ),
                            Div(
                                Label('Baz', _for='radio-button'),
                                RadioButton(name='radio-button', value='baz'),
                            ),
                            name='radio-button',
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
                f'changed node: {input_event.node._id}\nvalue: {pformat(input_event.data)}',
            )
