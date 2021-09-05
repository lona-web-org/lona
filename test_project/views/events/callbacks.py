from lona.html import (
    TextArea,
    CheckBox,
    TextInput,
    Button,
    Select,
    HTML,
    Div,
    H2,
    Br,
)

from lona import LonaView


class InputEventCallbackView(LonaView):
    def button(self, input_event):
        self.html.query_selector('div').set_text('Button was clicked')

    def check_box(self, input_event):
        self.html.query_selector('div').set_text(
            f'CheckBox was set to {input_event.node.value}',
        )

    def text_input(self, input_event):
        self.html.query_selector('div').set_text(
            f'TextInput was set to {input_event.node.value}',
        )

    def text_area(self, input_event):
        self.html.query_selector('div').set_text(
            f'TextArea was set to {input_event.node.value}',
        )

    def select(self, input_event):
        self.html.query_selector('div').set_text(
            f'Select was set to {input_event.node.value}',
        )

    def handle_request(self, request):
        self.html = HTML(
            H2('Input Event Callbacks'),
            Div('Nothing was changed yet'),
            Br(),

            Button('Button', _id='button'),
            Br(),

            CheckBox(_id='check-box'),
            Br(),

            TextInput(_id='text-input'),
            Br(),

            TextArea(_id='text-area'),
            Br(),

            Select(
                _id='select',
                values=[
                    ('option-1', 'Option 1'),
                    ('option-2', 'Option 2'),
                    ('option-3', 'Option 3'),
                ]
            ),
        )

        self.html.query_selector('#button').handle_click = self.button
        self.html.query_selector('#check-box').handle_change = self.check_box
        self.html.query_selector('#text-input').handle_change = self.text_input
        self.html.query_selector('#text-area').handle_change = self.text_area
        self.html.query_selector('#select').handle_change = self.select

        return self.html
