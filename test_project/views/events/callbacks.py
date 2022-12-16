from lona.html import (
    TextInput,
    TextArea,
    CheckBox,
    Select,
    Button,
    FOCUS,
    HTML,
    BLUR,
    Div,
    H2,
    Br,
)
from lona import View


class InputEventCallbackView(View):
    def button(self, input_event):
        self.html.query_selector('div').set_text('Button was clicked')

    def check_box(self, input_event):
        self.html.query_selector('div').set_text(
            f'CheckBox was set to {input_event.node.value}',
        )

    def handle_text_input(self, input_event):
        # focus / blur
        if input_event.name in ('focus', 'blur'):
            self.html.query_selector('div').set_text(
                f'TextInput is {input_event.name}ed',
            )

        # change
        else:
            self.html.query_selector('div').set_text(
                f'TextInput was set to {input_event.node.value}',
            )

    def handle_text_area(self, input_event):
        # focus / blur
        if input_event.name in ('focus', 'blur'):
            self.html.query_selector('div').set_text(
                f'TextArea is {input_event.name}ed',
            )

        # change
        else:
            self.html.query_selector('div').set_text(
                f'TextArea was set to {input_event.node.value}',
            )

    def handle_select(self, input_event):
        # focus / blur
        if input_event.name in ('focus', 'blur'):
            self.html.query_selector('div').set_text(
                f'Select is {input_event.name}ed',
            )

        # change
        else:
            self.html.query_selector('div').set_text(
                f'Select was set to {input_event.node.value}',
            )

    def handle_request(self, request):
        # text input
        text_input = TextInput(_id='text-input')

        text_input.events.add(FOCUS)
        text_input.events.add(BLUR)

        text_input.handle_change = self.handle_text_input
        text_input.handle_focus = self.handle_text_input
        text_input.handle_blur = self.handle_text_input

        # text area
        text_area = TextArea(_id='text-area')

        text_area.events.add(FOCUS)
        text_area.events.add(BLUR)

        text_area.handle_change = self.handle_text_area
        text_area.handle_focus = self.handle_text_area
        text_area.handle_blur = self.handle_text_area

        # select
        select = Select(
            _id='select',
            values=[
                ('option-1', 'Option 1'),
                ('option-2', 'Option 2'),
                ('option-3', 'Option 3'),
            ],
        )

        select.events.add(FOCUS)
        select.events.add(BLUR)

        select.handle_change = self.handle_select
        select.handle_focus = self.handle_select
        select.handle_blur = self.handle_select

        self.html = HTML(
            H2('Input Event Callbacks'),
            Div('Nothing was changed yet'),
            Br(),

            Button('Button', handle_click=self.button),
            Br(),

            CheckBox(handle_change=self.check_box),
            Br(),

            text_input,
            Br(),

            text_area,
            Br(),

            select,
        )

        return self.html
