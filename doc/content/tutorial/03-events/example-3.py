from lona_picocss.html import InlineButton, NumberInput, HTML, H1, P
from lona_picocss import install_picocss

from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class Index(View):
    def handle_request(self, request):
        first_number = 0
        second_number = 0
        number_input = NumberInput()

        # first number
        number_input.value = first_number

        html = HTML(
            H1('Enter A Number'),
            number_input,
            InlineButton('Enter'),
        )

        input_event = self.await_click(html=html)
        first_number = number_input.value

        # second number
        number_input.value = second_number

        html = HTML(
            H1('Enter A Second Number'),
            number_input,
            InlineButton('Enter'),
        )

        input_event = self.await_click(html=html)
        second_number = number_input.value

        # result
        return HTML(
            H1('Result'),
            P(f'{first_number} + {second_number} = {first_number+second_number}')
        )


if __name__ == '__main__':
    app.run()
