from lona_picocss.html import InlineButton, TextInput, HTML, H1
from lona_picocss import install_picocss

from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class Index(View):
    def handle_button_click(self, input_event):
        with self.html.lock:
            self.html[0].set_text(f'Hello {self.name.value}')
            self.name.remove()
            self.submit.remove()

    def handle_request(self, request):
        self.name = TextInput(placeholder='Name')

        self.submit = InlineButton(
            'Submit',
            handle_click=self.handle_button_click,
        )

        self.html = HTML(
            H1('Enter Your Name'),
            self.name,
            self.submit,
        )

        self.show(self.html)


app.run()
