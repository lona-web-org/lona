from lona_picocss import install_picocss
from lona.html import HTML, H1, H2, P
from lona import App, View

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class HelloWorldView(View):
    def handle_request(self, request):
        text = HTML(
            H1('Test SVG'),
            open('test.svg', 'r').read(),

            H2('HTML Special Characters'),
            P('Euro sign as entity name &euro;'),
            P('Euro sign in decimal &#8364;'),
            P('Euro sign in hexadecimal &#x20AC;'),
        )

        return text


app.run()