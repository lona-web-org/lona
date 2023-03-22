from lona.html.node import Node


class A(Node):
    TAG_NAME = 'a'

    def __init__(self, *args, interactive=None, **kwargs):
        super().__init__(*args, **kwargs)

        # This is necessary because 'interactive' uses 'ignore' internally.
        # If interactive were set to True by default ignore=True wouldn't
        # work as expected.
        if interactive is not None:
            self.interactive = interactive

    @property
    def interactive(self):
        return not self.ignore

    @interactive.setter
    def interactive(self, value):
        self.ignore = not value

    def set_href(self, href):
        self.attributes['href'] = str(href)

    def get_href(self, href):
        return self.attributes['href']


class Br(Node):
    TAG_NAME = 'br'
    SELF_CLOSING_TAG = True


class I(Node):  # NOQA: E742
    TAG_NAME = 'i'


class Small(Node):
    TAG_NAME = 'small'


class Span(Node):
    TAG_NAME = 'span'


class Strong(Node):
    TAG_NAME = 'strong'


class Sub(Node):
    TAG_NAME = 'sub'
