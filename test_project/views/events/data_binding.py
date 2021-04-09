from pprint import pformat

from lona.view import LonaView

from lona.html import (
    TextInput,
    CheckBox,
    TextArea,
    Select,
    HTML,
    Div,
    H1,
    Pre,
)


class DataBindingView(LonaView):
    def handle_request(self, request):
        check_box = CheckBox(bubble_up=True)
        text_input = TextInput(bubble_up=True)

        select = Select(
            values=[
                ('', '---'),
                ('option-a', 'Option A', True),
                ('option-b', 'Option B', True),
            ],
            bubble_up=True,
        )

        select_multiple = Select(
            values=[
                ('option-a', 'Option A', True),
                ('option-b', 'Option B', True),
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
            H1('Databinding'),
            Div(
                Div(
                    Div(check_box),
                    Div(text_input),
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

                    style={
                        'float': 'left',
                        'width': '50%',
                    },
                ),
            ),
        )

        while True:
            request.client.await_input_event(html=html)

            pre.set_text(
                pformat({
                    'check_box': check_box.value,
                    'text_input': text_input.value,
                    'select': select.value,
                    'select_multiple': select_multiple.value,
                    'text_area': text_area.value,
                })
            )
