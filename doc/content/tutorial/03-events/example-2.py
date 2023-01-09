from lona_picocss.html import InlineButton, Label, Span, Icon, HTML, Div, H1
from lona_picocss import install_picocss

from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


class Counter(Div):
    def __init__(self, value=0):
        super().__init__()

        self.nodes = [
            Label(
                InlineButton(Icon('minus-circle'), handle_click=self.decrease),
                ' ',
                Span(),
                ' ',
                InlineButton(Icon('plus-circle'), handle_click=self.increase),
            ),
        ]

        self.set_value(value)

    def set_value(self, value):
        with self.lock:
            self.query_selector('span').set_text(f'{value:03}')

    def get_value(self):
        with self.lock:
            return int(self.query_selector('span').get_text())

    def decrease(self, input_event):
        with self.lock:
            current_value = self.get_value()
            self.set_value(current_value - 1)

    def increase(self, input_event):
        with self.lock:
            current_value = self.get_value()
            self.set_value(current_value + 1)


@app.route('/')
class Index(View):
    def handle_click(self, input_event):
        input_event.node.set_text('Success!')

    def handle_request(self, request):
        return HTML(
            H1('Counter'),
            Counter(10),
            Counter(20),
            Counter(30),
        )


app.run()
