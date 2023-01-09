from lona_picocss.html import HTML, Div, H1
from lona_picocss import install_picocss

from lona.static_files import StyleSheet
from lona import View, App

app = App(__file__)

install_picocss(app, debug=True)


class RedColoredDiv(Div):

    # give the node the right id, in order for the CSS to work
    ID_LIST = [
        'red-colored',
    ]

    # this tells the frontend that this file has to be loaded
    # before the node can be rendered
    STATIC_FILES = [

        # all paths are relative to the file in which
        # the static files are defined in (this file)
        StyleSheet(
            name='red-colored-div',
            path='red-colored-div.css',
        ),
    ]


@app.route('/')
class Index(View):
    def handle_request(self, request):
        return HTML(
            H1('Custom CSS'),
            RedColoredDiv('Red Text'),
        )


app.run()

