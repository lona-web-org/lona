from lona.view import LonaView

from lona.html import (
    SelectNode,
    OptionNode,
    CHANGE,
    Widget,
    Button,
    HTML,
    Div,
    Pre,
    H2,
    P,
)


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
            '>> Widget({}).handle_input_event({})'.format(
                self.text,
                repr(input_event),
            )
        )

        if self.view.stop_at != self.text:
            return input_event


class EventBubblingView(LonaView):
    def handle_request(self, request):
        self.stop_at = None

        self.console = Pre(
            style={
                'background-color': 'lightgrey',
            },
        )

        html = HTML(
            H2('Event Bubbling'),
            Div(
                'Stop Event at ',
                SelectNode(
                    OptionNode(
                        '---',
                        value='',
                        selected=True,
                    ),
                    OptionNode(
                        'handle_input_event_root',
                        value='handle_input_event_root',
                    ),
                    OptionNode(
                        'Widget 1',
                        value='Widget 1',
                    ),
                    OptionNode(
                        'Widget 2',
                        value='Widget 2',
                    ),
                    OptionNode(
                        'Widget 3',
                        value='Widget 3',
                    ),
                    OptionNode(
                        'handle_input_event',
                        value='handle_input_event',
                    ),
                    events=[CHANGE],
                ),
            ),

            self.console,

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
                    )
                )
            )
        )

        while True:
            input_event = request.client.await_input_event(html=html)

            self.print('>> view.handle_request {}'.format(repr(input_event)))

    def clear(self):
        self.console.nodes.clear()

    def print(self, message):
        if not message.endswith('\n'):
            message += '\n'

        self.console.nodes.append(message)

    def handle_input_event_root(self, input_event):
        if input_event.type == 'change':
            self.stop_at = input_event.data

            return

        self.clear()

        self.print(
            '>> view.handle_input_event_root({})'.format(repr(input_event)))

        if self.stop_at != 'handle_input_event_root':
            return input_event

    def handle_input_event(self, input_event):
        self.print('>> view.handle_input_event({})'.format(repr(input_event)))

        if self.stop_at != 'handle_input_event':
            return input_event
