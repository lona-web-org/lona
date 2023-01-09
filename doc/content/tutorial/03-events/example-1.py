from lona_picocss.html import InlineButton, CLICK, HTML, H1, P
from lona_picocss import install_picocss

from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class Index(View):
    def handle_click(self, input_event):
        input_event.node.set_text('Success!')

    def handle_request(self, request):
        return HTML(
            H1('Click On Something'),

            # we tell Lona with `events=[CLICK]` that this node can
            # produces click events, and with `handle_click` which code
            # should be called when a click event is issued
            P('Click Me', events=[CLICK], handle_click=self.handle_click),

            # some nodes from the standard library come pre-configured with
            # events, set in `Node.EVENTS`
            InlineButton('Or Me', handle_click=self.handle_click),
        )


app.run()
