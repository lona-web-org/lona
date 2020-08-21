from lona.html.base import Node, Widget  # NOQA


# simple html nodes ###########################################################
class Html(Node):
    TAG_NAME = 'html'


class Head(Node):
    TAG_NAME = 'head'


class Body(Node):
    TAG_NAME = 'body'


class Nav(Node):
    TAG_NAME = 'nav'


class Main(Node):
    TAG_NAME = 'main'


class Section(Node):
    TAG_NAME = 'section'


class Script(Node):
    TAG_NAME = 'script'


class NoScript(Node):
    TAG_NAME = 'noscript'


class H1(Node):
    TAG_NAME = 'h1'


class H2(Node):
    TAG_NAME = 'h2'


class H3(Node):
    TAG_NAME = 'h3'


class H4(Node):
    TAG_NAME = 'h4'


class H5(Node):
    TAG_NAME = 'h5'


class H6(Node):
    TAG_NAME = 'h6'


class Div(Node):
    TAG_NAME = 'div'


class Span(Node):
    TAG_NAME = 'span'


class P(Node):
    TAG_NAME = 'p'


class Strong(Node):
    TAG_NAME = 'strong'


class Small(Node):
    TAG_NAME = 'small'


class Ul(Node):
    TAG_NAME = 'ul'


class Ol(Node):
    TAG_NAME = 'ol'


class Li(Node):
    TAG_NAME = 'li'


class Table(Node):
    TAG_NAME = 'table'


class THead(Node):
    TAG_NAME = 'thead'


class TBody(Node):
    TAG_NAME = 'tbody'


class TFood(Node):
    TAG_NAME = 'tfood'


class ColGroup(Node):
    TAG_NAME = 'colgroup'


class Tr(Node):
    TAG_NAME = 'tr'


class Th(Node):
    TAG_NAME = 'th'


class Td(Node):
    TAG_NAME = 'td'


# inputs ######################################################################
class Form(Node):
    TAG_NAME = 'form'


class Label(Node):
    TAG_NAME = 'label'


class Button(Node):
    TAG_NAME = 'button'

    LONA_ATTRIBUTES = {
        'clickable': True,
    }


class Input(Node):
    TAG_NAME = 'input'
    SINGLE_TAG = True


class TextInput(Input):
    ATTRIBUTES = {
        'type': 'text',
    }


class Checkbox(Input):
    ATTRIBUTES = {
        'type': 'checkbox',
    }


class Select(Node):
    TAG_NAME = 'select'


class Option(Node):
    TAG_NAME = 'option'


# complex html nodes ##########################################################
class Img(Node):
    TAG_NAME = 'img'
    SINGLE_TAG = True


class A(Node):
    TAG_NAME = 'a'

    def set_href(self, href):
        self.attributes['href'] = str(href)

    def get_href(self, href):
        return self.attributes['href']


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
