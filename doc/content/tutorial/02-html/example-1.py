from datetime import datetime

from lona_picocss import install_picocss

from lona.html import Strong, Span, HTML, H1, P
from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


@app.route('/')
class Index(View):
    def handle_request(self, request):
        html = HTML(
            H1('Clock'),
            P(
                Span('The current time is: '),
                Strong(str(datetime.now())),
            ),
        )

        return html


if __name__ == '__main__':
    app.run()
