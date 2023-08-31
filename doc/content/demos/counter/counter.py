import contextlib

from lona.html import NumberInput, Button, Span, HTML, H1
from lona import LonaView, LonaApp

app = LonaApp(__file__)


@app.route('/')
class CounterView(LonaView):
    def increase_counter(self, input_event):
        self.counter.set_text(
            int(self.counter.get_text()) + 1,
        )

    def decrease_counter(self, input_event):
        self.counter.set_text(
            int(self.counter.get_text()) - 1,
        )

    def set_counter(self, input_event):
        with contextlib.suppress(TypeError):
            self.counter.set_text(int(self.number_input.value))

    def handle_request(self, request):
        self.counter = Span('0')
        self.number_input = NumberInput(value=10, _style={'width': '3em'})

        return HTML(
            H1('Counter: ', self.counter),

            self.number_input,
            Button('Set', _id='set', handle_click=self.set_counter),

            Button(
                'Decrease',
                _style={'margin-left': '1em'},
                handle_click=self.decrease_counter,
            ),

            Button('Increase', handle_click=self.increase_counter),
        )


if __name__ == '__main__':
    app.run(port=8080)
