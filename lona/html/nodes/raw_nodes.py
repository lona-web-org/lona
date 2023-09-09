from lona.html.mixins import FrontendComponent
from lona.html import Div


class RawHTML(FrontendComponent, Div):
    TAG_NAME = 'div'
    WIDGET = 'lona.RawHtmlWidget'

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
