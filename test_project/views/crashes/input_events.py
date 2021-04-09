from datetime import datetime

from lona.html import Widget, Button, HTML, Div, Br, H1
from lona.view import LonaView


class CrashWidget(Widget):
    def __init__(self):
        self.nodes = [
            Button('Crash in widget'),
        ]

    def handle_input_event(self, input_event):
        raise ValueError('Success! Crash in widget')


class CrashingEventHandler(LonaView):
    def handle_request(self, request):

        handle_request_button = Button(
            'Crash in handle_request()',
            _id='handle_request',
        )

        handle_input_event_button = Button(
            'Crash in handle_input_event()',
            _id='handle_input_event',
        )

        handle_input_event_button.hide()

        html = HTML(
            H1('Crashing Event Handler'),
            Div(),
            Button('Start refresh loop', _id='refresh-loop'),
            Button('Stop view', _id='stop-view'),
            Br(),
            Br(),

            handle_request_button,

            Button(
                'Crash in handle_input_event_root()',
                _id='handle_input_event_root',
            ),

            handle_input_event_button,

            CrashWidget(),
        )

        input_event = request.client.await_input_event(html=html)

        if input_event.node_has_id('handle_request'):
            raise ValueError('Success! Crash in handle_request()')

        handle_request_button.hide()
        handle_input_event_button.show()

        if input_event.node_has_id('stop-view'):
            return html

        if input_event.node_has_id('refresh-loop'):
            while True:
                html[1].set_text(str((datetime.now())))

                request.client.show(html)

                request.view.sleep(1)

    def handle_input_event_root(self, input_event):
        if input_event.node_has_id('handle_input_event_root'):
            raise ValueError('Success! Crash in handle_input_event_root()')

        return input_event

    def handle_input_event(self, input_event):
        if input_event.node_has_id('handle_input_event'):
            raise ValueError('Success! Crash in handle_input_event()')

        return input_event
