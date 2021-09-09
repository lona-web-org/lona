from lona.html import NumberInput, Button, Span, HTML, H1
from lona import LonaView, LonaApp

app = LonaApp(__file__)


@app.route('/')
class CounterView(LonaView):
    def handle_request(self, request):
        counter = Span('0')
        number_input = NumberInput(value=10, _style={'width': '3em'})

        html = HTML(
            H1('Counter: ', counter),

            number_input,
            Button('Set', _id='set'),

            Button('Decrease', _id='decrease', _style={'margin-left': '1em'}),
            Button('Increase', _id='increase'),
        )

        while True:
            self.show(html)

            input_event = self.await_click()

            # increase
            if input_event.node_has_id('increase'):
                counter.set_text(
                    int(counter.get_text()) + 1,
                )

            # decrease
            elif input_event.node_has_id('decrease'):
                counter.set_text(
                    int(counter.get_text()) - 1,
                )

            # set
            elif input_event.node_has_id('set'):
                try:
                    counter.set_text(int(number_input.value))

                except TypeError:
                    pass


app.run(port=8080)
