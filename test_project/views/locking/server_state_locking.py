from datetime import datetime

from lona.html import Strong, Button, Span, Div, H1, Br
from lona import LonaView


class LockingView(LonaView):
    def handle_request(self, request):
        now = Span()
        self.message = Div('Button not clicked')
        self.button = Button('Button')

        self.html = Div(
            H1('Server State Locking View'),
            Div(Strong('Now: '), now),
            Br(),
            self.message,
            self.button,
        )

        while True:
            request.server.state['now'] = str(datetime.now())
            now.set_text(request.server.state['now'])
            request.client.show(self.html)

            request.view.sleep(1)

    def handle_input_event(self, input_event):
        with input_event.request.server.state.lock:
            self.message.set_text('Button clicked; Lock')
            input_event.request.client.show(self.html)

            input_event.request.view.sleep(2)

            self.message.set_text('Unlock')
            input_event.request.client.show(self.html)
