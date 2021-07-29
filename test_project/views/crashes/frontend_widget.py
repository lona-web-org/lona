from lona.static_files import Script
from lona.html import HTML, Widget
from lona.view import LonaView


class CrashingFrontendWidget(Widget):
    STATIC_FILES = [
        Script(
            name='CrashingFrontendWidget',
            path='crashing_frontend_widget.js',
        ),
    ]

    FRONTEND_WIDGET_CLASS = 'crashing_frontend_widget'


class CrashingFrontendWidgetView(LonaView):
    def handle_request(self, request):
        html = HTML(
            CrashingFrontendWidget(),
        )

        self.show(html)
