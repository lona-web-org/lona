from lona_picocss import install_picocss

from lona.html import HTML, H1, P
from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)

# set max threads to 10
app.settings.MAX_WORKER_THREADS = 10

# custom setting
app.settings.MY_CUSTOM_SETTING = 'foo'


@app.route('/')
class Index(View):
    def handle_request(self, request):
        my_custom_setting = self.server.settings.MY_CUSTOM_SETTING

        return HTML(
            H1('Hello World'),
            P(my_custom_setting),
        )


app.run()

