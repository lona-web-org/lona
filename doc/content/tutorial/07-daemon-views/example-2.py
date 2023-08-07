from lona_picocss.html import (
    InlineButton,
    NumberInput,
    Progress,
    Modal,
    Label,
    HTML,
    Grid,
    Pre,
    H3,
    H1,
    P,
)
from lona_picocss import install_picocss

from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class Index(View):
    def open_modal(self, input_event):
        with self.html.lock:
            self.modal.get_body().nodes = [
                H3('Stop Counter'),
                P('Are you sure you want to stop the counter?'),
            ]

            self.modal.get_footer().nodes = [
                InlineButton(
                    'Cancel',
                    secondary=True,
                    handle_click=lambda i: self.modal.close(),
                ),
                InlineButton(
                    'Stop',
                    handle_click=self.stop_counter,
                ),
            ]

            self.modal.open()

    def stop_counter(self, input_event):
        self.modal.close()
        self.running = False

    def handle_request(self, request):

        # daemonize view
        self.is_daemon = True

        # wait for start
        self.limit = NumberInput(value=10)

        self.html = HTML(
            H1('Counter'),
            Grid(
                Label(
                    'Limit',
                    self.limit,
                ),
                InlineButton('Start'),
            ),
        )

        self.await_click(html=self.html)

        # count to limit
        self.running = True
        self.modal = Modal()

        progress = Progress(value=0)

        pre = Pre(
            style={
                'height': f'{int(self.limit.value) + 4}em',
            },
        )

        self.html = HTML(
            H1('Counter'),
            progress,
            pre,
            InlineButton(
                'Stop',
                handle_click=self.open_modal,
                style={
                    'float': 'right',
                },
            ),
            self.modal,
        )

        for i in range(1, int(self.limit.value) + 1):

            # check if view should stop
            if not self.running:
                pre.write_line('view stopped')
                self.show(self.html)

                return

            progress.value = 100 / int(self.limit.value) * i
            pre.write_line(f'Counting to {i}')

            self.show(self.html)
            self.sleep(1)

        # finish
        pre.write_line('finish')

        return self.html


if __name__ == '__main__':
    app.run()
