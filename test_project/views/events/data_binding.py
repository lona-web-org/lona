from pprint import pformat

from lona.view import LonaView

from lona.html import (
    NumberInput,
    TextInput,
    CheckBox,
    TextArea,
    Button,
    Select,
    HTML,
    Div,
    H2,
    Pre,
)


class DataBindingView(LonaView):
    def handle_request(self, request):
        check_box = CheckBox(bubble_up=True)
        text_input = TextInput(bubble_up=True)
        int_number_input = NumberInput(bubble_up=True, value=10, step=2)
        float_number_input = NumberInput(bubble_up=True, value=12.3, step=0.1)

        select = Select(
            values=[
                ('', '---'),
                ('option-a', 'Option A', True),
                ('option-b', 'Option B', False),
            ],
            bubble_up=True,
        )

        select_multiple = Select(
            values=[
                ('option-a', 'Option A', True),
                ('option-b', 'Option B', False),
                ('option-c', 'Option C'),
            ],
            bubble_up=True,
            multiple=True,
        )

        text_area = TextArea(bubble_up=True)

        pre = Pre(
            '{}',
            style={
                'background-color': 'lightgrey',
            },
        )

        html = HTML(
            H2('Databinding'),
            Div(
                Div(
                    Div(check_box),
                    Div(text_input),
                    Div(int_number_input),
                    Div(float_number_input),
                    Div(select),
                    Div(select_multiple),
                    Div(text_area),

                    style={
                        'float': 'left',
                        'width': '50%',
                    },
                ),
                Div(
                    pre,
                    Button('Set texts', _id='set-texts'),
                    Button('Daemonize', _id='daemonize'),
                    Button('Stop', _id='stop'),

                    style={
                        'float': 'left',
                        'width': '50%',
                    },
                ),
            ),
        )

        while True:
            input_event = self.await_input_event(html=html)

            if input_event.node_has_id('set-texts'):
                text_input.value = 'test'
                text_area.value = 'test'

            elif input_event.node_has_id('daemonize'):
                self.daemonize()

            elif input_event.node_has_id('stop'):
                return 'View Stopped'

            else:
                pre.set_text(
                    pformat({
                        'check_box': check_box.value,
                        'text_input': text_input.value,
                        'int_number_input': int_number_input.value,
                        'float_number_input': float_number_input.value,
                        'select': select.value,
                        'select_multiple': select_multiple.value,
                        'text_area': text_area.value,
                    })
                )
