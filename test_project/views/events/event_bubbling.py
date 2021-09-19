from lona.html import Widget, Select, Button, HTML, Pre, Div, H2, P
from lona.view import LonaView


class BubblingWidget(Widget):
    def __init__(self, view, text, *nodes):
        self.text = text
        self.view = view

        self.nodes = [
            Div(
                style={
                    'padding': '0px 5px 5px 10px',
                    'border': '1px solid black',
                    'margin-top': '10px',
                },
                nodes=[
                    P(text),
                    Button('Click Me'),
                    *nodes,
                ],
            ),
        ]

    def handle_input_event(self, input_event):
        self.view.print(
            f'>> Widget({self.text}).handle_input_event({input_event!r})',
        )

        if self.view.select.value != self.text:
            return input_event


class EventBubblingView(LonaView):
    def handle_request(self, request):
        html = HTML(
            H2('Event Bubbling'),
            Div(
                'Stop Event at ',
                Select(
                    values=[
                        ('', '---', True),
                        ('handle_input_event_root', 'handle_input_event_root'),
                        ('Widget 1', 'Widget 1'),
                        ('Widget 2', 'Widget 2'),
                        ('Widget 3', 'Widget 3'),
                    ],
                ),
            ),

            # console
            Pre(
                style={
                    'background-color': 'lightgrey',
                },
            ),

            Button('Click Me'),
            BubblingWidget(
                self,
                'Widget 1',
                BubblingWidget(
                    self,
                    'Widget 2',
                    BubblingWidget(
                        self,
                        'Widget 3',
                    ),
                ),
            ),
        )

        self.select = html.query_selector('select')
        self.console = html.query_selector('pre')

        while True:
            input_event = self.await_input_event(html=html)

            self.print(f'>> view.handle_request {input_event!r}')

    def clear(self):
        self.console.nodes.clear()

    def print(self, message):
        if not message.endswith('\n'):
            message += '\n'

        self.console.nodes.append(message)

    def handle_input_event_root(self, input_event):
        self.clear()

        self.print(f'>> view.handle_input_event_root({input_event!r})')

        if self.select.value != 'handle_input_event_root':
            return input_event

    def handle_input_event(self, input_event):
        self.print(f'>> view.handle_input_event({input_event!r})')

        if self.select.value != 'handle_input_event':
            return input_event
