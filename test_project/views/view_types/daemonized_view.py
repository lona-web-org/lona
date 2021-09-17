from lona.html import Button, Div, H2
from lona.view import LonaView


class DaemonizedView(LonaView):
    def handle_request(self, request, name='blank'):
        message = Div('View not started yet')
        log = Div()
        start = Button('Start')
        start_daemonized = Button('Start daemonized')

        html = Div(
            H2(f'Daemonized View (name={name})'),
            message,
            log,
            start,
            start_daemonized,
        )

        input_event = self.await_input_event(html=html)

        if input_event.node == start_daemonized:
            self.daemonize()

            message.set_text('View started daemonized')

        else:
            message.set_text('View started normal')

        for i in range(15):
            log.set_text(f'Counting ({i+1}/15)')
            self.show(html)

            self.sleep(1)

        message.set_text('View stopped')
        self.show(html)
