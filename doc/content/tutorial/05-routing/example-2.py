from lona_picocss.html import InlineButton, TextInput, HTML, H1, P
from lona_picocss import install_picocss

from lona import RedirectResponse, View, App

app = App(__file__)

install_picocss(app, debug=True)


# give this route the name 'greet-view'
@app.route('/hello/<name>', name='greet-view')
class GreetView(View):
    def handle_request(self, request):
        name = request.match_info['name']

        return HTML(
            H1(f'Hello {name}'),
            P('How are you?'),
        )


@app.route('/')
class Index(View):
    def handle_button_click(self, input_event):
        return RedirectResponse(

            # use route name instead of the hard coded value
            self.server.reverse('greet-view', name=self.text_input.value),
        )

    def handle_request(self, request):
        self.text_input = TextInput(
            placeholder='Name',
        )

        return HTML(
            H1('Enter Your Name'),
            self.text_input,
            InlineButton('Greet Me', handle_click=self.handle_button_click),
        )


if __name__ == '__main__':
    app.run()
