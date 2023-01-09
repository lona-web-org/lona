from lona_picocss import install_picocss

from lona.html import HTML, H1, P
from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class Index(View):
    def handle_request(self, request):
        return HTML(
            H1('Hello World'),
            P('Lorem Ipsum'),
        )


app.run()
