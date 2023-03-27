from lona.static_files import SORT_ORDER, Script
from lona.html.node import Node


class RawHTML(Node):
    TAG_NAME = 'div'
    WIDGET = 'lona.RawHtmlWidget'

    STATIC_FILES = [
        Script(
            name='_lona/widgets.js',
            path='widgets.js',
            sort_order=SORT_ORDER.FRAMEWORK,
        ),
    ]

    def __init__(self, inner_html='', **kwargs):
        super().__init__(**kwargs)

        self.inner_html = inner_html
        self.nodes._freeze()

    @property
    def inner_html(self):
        return self.widget_data['inner_html']

    @inner_html.setter
    def inner_html(self, value):
        self.widget_data['inner_html'] = value

    def __str__(self):
        return super().__str__(node_string=self.inner_html)
