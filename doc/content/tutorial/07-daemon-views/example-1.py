from lona_picocss.html import InlineButton, TextArea, Span, HTML, Div, H1, Br
from lona_picocss import install_picocss

from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class Index(View):
    STOP_DAEMON_WHEN_VIEW_FINISHES = False

    def handle_button_click(self, input_event):
        with self.html.lock:
            span = self.html.query_selector('span#counter')
            span.set_text(int(span.get_text()) + 1)

    def handle_request(self, request):

        # daemonize view
        self.is_daemon = True

        self.html = HTML(
            H1('Daemonized View'),
            Div(
                'Counter: ',
                Span('10', _id='counter'),
                ' ',
                InlineButton(
                    'Increment',
                    handle_click=self.handle_button_click,
                ),
                Br(),
                Br(),
            ),
            TextArea(placeholder='TextArea')
        )

        return self.html


app.run()
