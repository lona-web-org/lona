from datetime import datetime

from lona.html import NumberInput, Button, Table, HTML, Tr, Th, Td, H2
from lona import View


class SleepTestView(View):
    def handle_request(self, request):

        # setup global state
        if 'id' in request.GET:
            self.view_id = request.GET['id']

        else:
            self.view_id = 'sleep-test-view'

        self.server.state[self.view_id] = {}

        # setup html
        seconds = NumberInput(value=1, id='seconds')
        button = Button('Sleep', id='sleep')

        self.html = HTML(
            H2('View.sleep()'),

            Table(
                Tr(
                    Th('State:'),
                    Td(_id='state'),
                ),
                Tr(
                    Th('Started:'),
                    Td(_id='started'),
                ),
                Tr(
                    Th('Stopped:'),
                    Td(_id='stopped'),
                ),
            ),
            seconds,
            button,
        )

        self.set_state(sleeping=False, initial=True)

        # main loop
        while True:
            self.show(self.html)
            self.await_click(button)

            self.set_state(sleeping=True)
            self.show(self.html)

            self.sleep(seconds.value)
            self.set_state(sleeping=False)

    def set_state(self, sleeping, initial=False):
        with self.html.lock:
            state = self.html.query_selector('#state')
            started = self.html.query_selector('#started')
            stopped = self.html.query_selector('#stopped')

            # html
            if sleeping:
                state.set_text('Sleeping')
                started.set_text(str(datetime.now()))
                stopped.set_text('-')

            else:
                state.set_text('Waiting for start')

                if initial:
                    started.set_text('-')
                    stopped.set_text('-')

                else:
                    stopped.set_text(str(datetime.now()))

            # server
            if not self.view_id:
                return

            self.server.state[self.view_id]['state'] = state.get_text()
            self.server.state[self.view_id]['started'] = started.get_text()
            self.server.state[self.view_id]['stopped'] = stopped.get_text()

    def on_cleanup(self) -> None:
        if self.view_id:
            self.server.state.pop(self.view_id)
