from lona.static_files import Script
from lona.html import HTML, Div
from lona.view import LonaView


class CrashingWidgetNode(Div):
    STATIC_FILES = [
        Script(
            name='CrashingWidget',
            path='crashing_widget.js',
        ),
    ]

    WIDGET = 'crashing_widget'


class CrashingWidgetView(LonaView):
    def handle_request(self, request):
        html = HTML(
            CrashingWidgetNode(),
        )

        self.show(html)
