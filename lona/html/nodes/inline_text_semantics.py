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


class Abbr(Node):
    TAG_NAME = 'abbr'


class B(Node):
    TAG_NAME = 'b'


class Bdi(Node):
    TAG_NAME = 'bdi'


class Bdo(Node):
    TAG_NAME = 'bdo'


class Br(Node):
    TAG_NAME = 'br'
    SELF_CLOSING_TAG = True


class Cite(Node):
    TAG_NAME = 'cite'


class Code(Node):
    TAG_NAME = 'code'


class Data(Node):
    TAG_NAME = 'data'


class Dfn(Node):
    TAG_NAME = 'dfn'


class Em(Node):
    TAG_NAME = 'em'


class I(Node):  # NOQA: E742
    TAG_NAME = 'i'


class Kbd(Node):
    TAG_NAME = 'kbd'


class Mark(Node):
    TAG_NAME = 'mark'


class Q(Node):
    TAG_NAME = 'q'


class Rp(Node):
    TAG_NAME = 'rp'


class Rt(Node):
    TAG_NAME = 'rt'


class Ruby(Node):
    TAG_NAME = 'ruby'


class S(Node):
    TAG_NAME = 's'


class Samp(Node):
    TAG_NAME = 'samp'


class Small(Node):
    TAG_NAME = 'small'


class Span(Node):
    TAG_NAME = 'span'


class Strong(Node):
    TAG_NAME = 'strong'


class Sub(Node):
    TAG_NAME = 'sub'


class Sup(Node):
    TAG_NAME = 'sup'


class Time(Node):
    TAG_NAME = 'time'


class U(Node):
    TAG_NAME = 'u'


class Var(Node):
    TAG_NAME = 'var'


class Wbr(Node):
    TAG_NAME = 'wbr'
    SELF_CLOSING_TAG = True
