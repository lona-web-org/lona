from datetime import datetime
import time

from lona.html import Strong, Button, Span, Div, H1, Br


class LockingView:
    def handle_request(self, request):
        now = Span()
        self.message = Div('Button not clicked')
        self.button = Button('Button')

        self.html = Div(
            H1('Locking View'),
            Div(Strong('Now: '), now),
            Br(),
            self.message,
            self.button,
        )

        while True:
            now.set_text(datetime.now())
            request.client.show(self.html)

            time.sleep(1)

    def handle_input_event(self, request, input_event):
        with self.html.lock():
            self.message.set_text('Button clicked; Lock')
            request.client.show(self.html)

            time.sleep(2)

            self.message.set_text('Unlock')
            request.client.show(self.html)
