from lona.html import HTML, Div, H1, A, TextInput, Widget
from lona.static_files import Script, SORT_ORDER, StyleSheet
from lona import LonaView, LonaApp

app = LonaApp(__file__)

app.settings.STATIC_DIRS = [
    'static',
]


class AutoCompleteInput(Widget):
    FRONTEND_WIDGET_CLASS = 'AutoCompleteWidget'

    STATIC_FILES = [
        StyleSheet(
            name='jquery-ui.css',
            path='jquery-ui.css',
            url='jquery-ui.css',
            sort_order=SORT_ORDER.FRAMEWORK,
        ),
        Script(
            name='jquery.js',
            path='jquery.js',
            url='jquery.js',
            sort_order=SORT_ORDER.FRAMEWORK,
        ),
        Script(
            name='jquery-ui.js',
            path='jquery-ui.js',
            url='jquery-ui.js',
            sort_order=SORT_ORDER.FRAMEWORK,
        ),
        Script(
            name='autocomplete_widget.js',
            path='autocomplete_widget.js',
            url='autocomplete_widget.js',
            sort_order=SORT_ORDER.LIBRARY,
        ),
    ]

    def __init__(self, completer=lambda term: []):
        self.input_node = TextInput(bubble_up=True)

        self.nodes = [
            self.input_node,
        ]

        self.data = {
            'results': [],
        }

        self.completer = completer

    def handle_input_event(self, input_event):
        with self.lock:
            if input_event.name != 'autocomplete-request':
                return

            with self.lock:
                results = self.completer(input_event.data['term'])

                if not isinstance(results, list):
                    raise ValueError('results have to be a list')

                self.data['results'] = [str(result) for result in results]


@app.route('/')
class NoneInteractiveView(LonaView):
    def complete(self, term):
        words = [
            'foo',
            'foobar',
            'foobaz',
            'bar',
            'baz',
            'bazbar',
        ]

        return [
            word for word in words
            if word.startswith(term)
        ]

    def handle_request(self, request):
        return HTML(
            H1('AutoComplete'),
            AutoCompleteInput(completer=self.complete),
        )


app.run(port=8080)
