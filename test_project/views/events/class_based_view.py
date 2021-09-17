from lona.html import Button, Div, Br, HTML, H2
from lona.view import LonaView


class ClassBasedView(LonaView):
    def handle_request(self, request):
        self.message = Div('Nothing clicked yet')

        self.html = HTML(
            H2('Class Based View'),
            self.message,
            Br(),
            Button('handle_input_event_root()', _id='handle_input_event_root'),
            Button('handle_input_event()', _id='handle_input_event'),
            Button('handle_request()', _id='handle_request'),
            Br(),
            Button('Stop View', _id='stop_view')
        )

        while True:
            input_event = self.await_click(
                self.html[-3],
                self.html[-1],
                html=self.html,
            )

            if input_event.node == self.html[-1]:
                self.message.set_text('View Stopped')
                self.show(self.html)

                return

            self.message.set_text(
                'handled by handle_request()')

    def handle_input_event_root(self, input_event):
        if input_event.node_has_id('handle_input_event_root'):
            self.message.set_text(
                'handled by handle_input_event_root()')

        else:
            return input_event

    def handle_input_event(self, input_event):
        if input_event.node_has_id('handle_input_event'):
            self.message.set_text(
                'handled by handle_input_event()')

        else:
            return input_event
