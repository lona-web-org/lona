from datetime import datetime

from lona.html import Button, HTML, Div, H2, Br
from lona.view import View


class Counter(Div):
    def __init__(self, *nodes):
        self.button = Button('1')

        self.nodes = [
            self.button,
        ]

    def handle_input_event(self, input_event):
        self.button.set_text(int(str(self.button[0]))+1)


class NodeEventHandlerView(View):
    def handle_request(self, request):
        message = Div('Button not clicked yet')

        html = HTML(
            H2('Node Event Handler'),
            message,
            Br(),
            Counter(),
            Button('Button'),
            Br(),
            Br(),
            Button('Stop View', _id='stop_view'),
        )

        while True:
            input_event = self.await_input_event(html=html)

            if input_event.node.has_id('stop_view'):
                message.set_text('View Stopped')
                self.show(html)

                return

            message.set_text(f'Button clicked at {datetime.now()}')
