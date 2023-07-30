# hello-world.py

from lona_picocss import install_picocss

from lona.html import HTML, H1
from lona import View, App

app = App(__file__)

install_picocss(app)  # optional

app.settings.MAX_RUNTIME_THREADS = 50
app.settings.MAX_WORKER_THREADS = 100
app.settings.MAX_STATIC_THREADS = 20


@app.route('/')
class Index(View):
    def handle_request(self, request):
        return HTML(
            H1('Hello World'),
        )


app.run(host='0.0.0.0', port=8080)
