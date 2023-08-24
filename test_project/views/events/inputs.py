import datetime
import pprint
import html

from lona.html import (
    NumberInput,
    TextInput,
    TextArea,
    CheckBox,
    Select2,
    Option2,
    Select,
    Button,
    Table,
    FOCUS,
    CLICK,
    HTML,
    BLUR,
    Pre,
    Div,
    Tr,
    Td,
    H3,
    H2,
    Br,
    A,
)
from lona import RedirectResponse, View


class Console(Pre):
    STYLE = {
        'background-color': 'lightgrey',
        'width': '100%',
        'min-height': '20em',
        'padding': '0',
        'margin': '0',
        'overflow': 'auto',
    }


class LeftCol(Div):
    STYLE = {
        'min-height': '1px',
        'float': 'left',
        'width': 'calc(50% - 5px)',
    }


class RightCol(Div):
    STYLE = {
        'min-height': '1px',
        'float': 'right',
        'width': 'calc(50% - 5px)',
    }


class InputsView(View):

    # actions
    def reset_console(self, input_event=None):
        self.console.set_text('[EMPTY]')

    def run_show(self, input_event=None):
        self.show()

    def prefill_inputs(self, input_event=None):
        self.text_input.value = 'Test Text'
        self.number_input.value = 1
        self.check_box.value = True
        self.text_area.value = 'Test Text\nTest Text'
        self.select.value = '2.0'
        self.select2.value = 2.0
        self.multi_select.value = ['1', '2.0']
        self.multi_select2.value = [1, 2.0]

    def reset_inputs(self, input_event=None):
        return RedirectResponse('.')

    # event handler
    def handle_event(self, input_event):
        self.server.state[self.name]['event'] = input_event

        self.console.set_text(
            f'Time: {datetime.datetime.now()}\n'
            f'Event Type: {html.escape(str(input_event.type))}\n'
            f'Node Type: {html.escape(str(type(input_event.node)))}\n'
            f'Node ID: {input_event.node.id}\n'
            f'Value: {repr(getattr(input_event.node, "value", None))}\n\n'
            f'Event Data: \n{pprint.pformat(input_event.data)}',
        )

    def handle_request(self, request):
        self.console = Console(_id='console')

        # clickable nodes
        self.button = Button(
            'Button',
            handle_click=self.handle_event,
            _id='button',
        )

        self.link = A(
            'Link',
            href='/',
            events=[CLICK],
            handle_click=self.handle_event,
            _id='link',
        )

        self.div = Div(
            'Div',
            events=[CLICK],
            handle_click=self.handle_event,
            _id='div',
            style={
                'border': '1px solid black',
                'cursor': 'pointer',
            },
        )

        # input nodes
        self.text_input = TextInput(
            handle_change=self.handle_event,
            _id='text-input',
        )

        self.number_input = NumberInput(
            handle_change=self.handle_event,
            _id='number-input',
        )

        self.check_box = CheckBox(
            handle_change=self.handle_event,
            _id='check-box',
        )

        self.text_area = TextArea(
            handle_change=self.handle_event,
            _id='text-area',
        )

        self.select = Select(
            values=[
                (1, 'Option 1'),
                (2.0, 'Option 2'),
                ('3', 'Option 3'),
            ],
            handle_change=self.handle_event,
            _id='select',
        )

        self.select2 = Select2(
            Option2('Option 1', value=1),
            Option2('Option 2', value=2.0),
            Option2('Option 3', value='3'),
            handle_change=self.handle_event,
            _id='select-2',
        )

        self.multi_select = Select(
            values=[
                (1, 'Option 1'),
                (2.0, 'Option 2'),
                ('3', 'Option 3'),
            ],
            multiple=True,
            handle_change=self.handle_event,
            _id='multi-select',
        )

        self.multi_select2 = Select2(
            Option2('Option 1', value=1),
            Option2('Option 2', value=2.0),
            Option2('Option 3', value='3'),
            multiple=True,
            handle_change=self.handle_event,
            _id='multi-select-2',
        )

        # focus / blur nodes
        self.text_input_focus = TextInput(
            events=[FOCUS],
            handle_focus=self.handle_event,
            _id='text-input-focus',
        )

        self.text_input_blur = TextInput(
            events=[BLUR],
            handle_blur=self.handle_event,
            _id='text-input-blur',
        )

        # setup html
        self.html = HTML(
            H2('Events'),

            LeftCol(
                H3('Click Events'),
                Table(
                    Tr(
                        Td('Button', width='200px'),
                        Td(self.button),
                    ),
                    Tr(
                        Td('Link', width='200px'),
                        Td(self.link),
                    ),
                    Tr(
                        Td('Clickable Div', width='200px'),
                        Td(self.div),
                    ),
                ),

                H3('Change Events'),
                Table(
                    Tr(
                        Td('TextInput', width='200px'),
                        Td(self.text_input),
                    ),
                    Tr(
                        Td('NumberInput', width='200px'),
                        Td(self.number_input),
                    ),
                    Tr(
                        Td('CheckBox', width='200px'),
                        Td(self.check_box),
                    ),
                    Tr(
                        Td('TextArea', width='200px'),
                        Td(self.text_area),
                    ),
                    Tr(
                        Td('Select', width='200px'),
                        Td(self.select),
                    ),
                    Tr(
                        Td('Select2', width='200px'),
                        Td(self.select2),
                    ),
                    Tr(
                        Td('Multi Select', width='200px'),
                        Td(self.multi_select),
                    ),
                    Tr(
                        Td('Multi Select2', width='200px'),
                        Td(self.multi_select2),
                    ),
                ),

                H3('Focus Events'),
                Table(
                    Tr(
                        Td('TextInput', width='200px'),
                        Td(self.text_input_focus),
                    ),
                ),

                H3('Blur Events'),
                Table(
                    Tr(
                        Td('TextInput', width='200px'),
                        Td(self.text_input_blur),
                    ),
                ),

            ),

            RightCol(
                self.console,
                Br(),
                Div(
                    Button(
                        'Prefill Inputs',
                        handle_click=self.prefill_inputs,
                        _id='prefill-inputs',
                    ),
                    Button(
                        'Reset Inputs',
                        handle_click=self.reset_inputs,
                        _id='reset-inputs',
                    ),
                    Button(
                        'Reset Console',
                        handle_click=self.reset_console,
                        _id='reset-console',
                    ),
                    Button(
                        'Run Show',
                        handle_click=self.run_show,
                        _id='run-show',
                    ),
                ),
            ),
        )

        self.reset_console()

        # server state
        self.name = request.GET.get('context-name', 'events')

        self.server.state[self.name] = {
            'event': None,

            # clickable nodes
            '#button': self.button,
            '#link': self.link,
            '#div': self.div,

            # input nodes
            '#text-input': self.text_input,
            '#number-input': self.number_input,
            '#check-box': self.check_box,
            '#text-area': self.text_area,
            '#select': self.select,
            '#select-2': self.select2,
            '#multi-select': self.multi_select,
            '#multi-select-2': self.multi_select2,

            # focus / blur nodes
            '#text-input-focus': self.text_input_focus,
            '#text-input-blur': self.text_input_blur,
        }

        # prefill
        if 'prefill' in request.GET:
            self.prefill_inputs()

        return self.html
