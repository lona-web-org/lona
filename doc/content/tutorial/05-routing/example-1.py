from lona_picocss.html import InlineButton, TextInput, HTML, H1, P
from lona_picocss import install_picocss

from lona import RedirectResponse, View, App

app = App(__file__)

install_picocss(app, debug=True)


# setup the route
@app.route('/hello/<name>')
class GreetView(View):
    def handle_request(self, request):

        # all url args and the route are available in the
        # request object
        name = request.match_info['name']

        return HTML(
            H1(f'Hello {name}'),
            P('How are you?'),
        )


# index view
@app.route('/')
class Index(View):
    def handle_button_click(self, input_event):

        # redirect to the view with the special route
        return RedirectResponse(
            f'/hello/{self.text_input.value}'
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
