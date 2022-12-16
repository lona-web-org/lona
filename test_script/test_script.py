from datetime import datetime

from lona.html import HTML, Div, H1, A
from lona import LonaApp, View

app = LonaApp(__file__)

app.settings.MAX_WORKER_THREADS = 10

app.settings.STATIC_DIRS = [
    'static',
]


@app.middleware
class MyMiddleware:
    def handle_request(self, data):
        print('>> middleware running')

        return data


@app.frontend_view
class FrontendView(View):
    def handle_request(self, request):
        print('>> running frontend')

        return {
            'template': self.server.settings.FRONTEND_TEMPLATE,
        }


@app.route('/')
class Home(View):
    def handle_request(self, request):
        return """
            <h1>Lona Test Script</h1>
            <ul>
                <li><a href="/interactive-view/">Interactive View</a></li>
                <li><a href="/non-interactive-view/">Non Interactive View</a></li>
            </ul>
        """


@app.route('/interactive-view/')
class InteractiveView(View):
    def handle_request(self, request):
        timestamp = Div()

        html = HTML(
            H1('Interactive View'),
            A('Home', href='/'),
            timestamp,
        )

        while True:
            timestamp.set_text(str(datetime.now()))

            self.show(html)

            self.sleep(1)


@app.route('/non-interactive-view/', interactive=False)
class NoneInteractiveView(View):
    def handle_request(self, request):
        return """
            <h1>Non Interactive View</h1>
            <a href="/">Home</a>
        """


app.run(port=8080)
