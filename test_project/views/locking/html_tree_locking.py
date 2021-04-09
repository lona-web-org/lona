from datetime import datetime

from lona.html import Strong, Button, Span, Div, H1, Br
from lona.view import LonaView


class LockingView(LonaView):
    def handle_request(self, request):
        now = Span()
        self.message = Div('Button not clicked')
        self.button = Button('Button')

        self.html = Div(
            H1('HTML Tree Locking View'),
            Div(Strong('Now: '), now),
            Br(),
            self.message,
            self.button,
        )

        while True:
            now.set_text(datetime.now())
            request.client.show(self.html)

            request.view.sleep(1)

    def handle_input_event(self, input_event):
        with self.html.lock:
            self.message.set_text('Button clicked; Lock')
            input_event.request.client.show(self.html)

            input_event.request.view.sleep(2)

            self.message.set_text('Unlock')
            input_event.request.client.show(self.html)
