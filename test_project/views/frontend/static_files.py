from lona.static_files import StyleSheet
from lona.html import HTML, H2, P
from lona.view import LonaView


class BlueP(P):
    CLASS_LIST = [
        'blue-p',
    ]

    STATIC_FILES = [
        StyleSheet(
            name='node-styles',
            path='node-styles.css',
        ),
    ]


class StaticFilesView(LonaView):
    STATIC_FILES = [
        StyleSheet(
            name='view-styles',
            path='view-styles.css',
        ),
    ]

    def handle_request(self, request):
        return HTML(
            H2('Static Files'),
            P(
                'This view tests the delivery of static files that are '
                'defined in Nodes.STACIC_FILES or LonaView.STATIC_FILES',
            ),
            BlueP('This paragraph should be blue due node-styles.css'),
            P(
                'This paragraph should be blue due view-styles.css',
                _class='red-p',
            ),
        )
