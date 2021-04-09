from datetime import datetime

from lona.html import HTML, Button, Widget, Div, Br, H1
from lona.view import LonaView


class Counter(Widget):
    def __init__(self, *nodes):
        self.button = Button('1')

        self.nodes = [
            self.button,
        ]

    def handle_input_event(self, input_event):
        self.button.set_text(int(str(self.button[0]))+1)


class WidgetEventHandlerView(LonaView):
    def handle_request(self, request):
        message = Div('Button not clicked yet')

        html = HTML(
            H1('Widget Event Handler'),
            message,
            Br(),
            Counter(),
            Button('Button'),
            Br(),
            Br(),
            Button('Stop View', _id='stop_view'),
        )

        while True:
            input_event = request.client.await_input_event(html=html)

            if input_event.node.has_id('stop_view'):
                message.set_text('View Stopped')
                request.client.show(html)

                return

            message.set_text('Button clicked at {}'.format(datetime.now()))
