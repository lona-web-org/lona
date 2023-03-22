from lona.html.node import Node


class BlockQuote(Node):
    TAG_NAME = 'blockquote'


class Dd(Node):
    TAG_NAME = 'dd'


class Div(Node):
    TAG_NAME = 'div'


class Dl(Node):
    TAG_NAME = 'dl'


class Dt(Node):
    TAG_NAME = 'dt'


class FigCaption(Node):
    TAG_NAME = 'figcaption'


class Figure(Node):
    TAG_NAME = 'figure'


class Hr(Node):
    TAG_NAME = 'hr'
    SELF_CLOSING_TAG = True


class Li(Node):
    TAG_NAME = 'li'


class Menu(Node):
    TAG_NAME = 'menu'


class Ol(Node):
    TAG_NAME = 'ol'


class P(Node):
    TAG_NAME = 'p'


class Pre(Node):
    TAG_NAME = 'pre'

    def write(self, string):
        string = str(string)

        if len(self.nodes) > 0 and isinstance(self.nodes[-1], str):
            self.nodes[-1] = self.nodes[-1] + string

        else:
            self.nodes.append(string)

    def write_line(self, string):
        string = str(string) + '\n'

        self.nodes.append(string)


class Ul(Node):
    TAG_NAME = 'ul'
