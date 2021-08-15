from lona.events.event_types import CLICK
from lona.html.widget import Widget  # NOQA
from lona.html.node import Node


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


class I(Node):  # NOQA
    TAG_NAME = 'i'


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


class Canvas(Node):
    TAG_NAME = 'canvas'


class Hr(Node):
    TAG_NAME = 'hr'
    SELF_CLOSING_TAG = True


class Br(Node):
    TAG_NAME = 'br'
    SELF_CLOSING_TAG = True


# inputs ######################################################################
class Form(Node):
    TAG_NAME = 'form'


class Fieldset(Node):
    TAG_NAME = 'form'


class Label(Node):
    TAG_NAME = 'label'


class Button(Node):
    TAG_NAME = 'button'
    EVENTS = [CLICK]

    @property
    def disabled(self):
        return 'disabled' in self.attributes

    @disabled.setter
    def disabled(self, new_value):
        with self.document.lock:
            new_value = bool(new_value)

            if new_value:
                if 'disabled' not in self.attributes:
                    self.attributes['disabled'] = 'True'
            else:
                if 'disabled' in self.attributes:
                    del self.attributes['disabled']


class InputNode(Node):
    TAG_NAME = 'input'
    SELF_CLOSING_TAG = True


class Submit(InputNode):
    ATTRIBUTES = {
        'type': 'submit',
        'value': 'Submit',
    }


class Reset(InputNode):
    ATTRIBUTES = {
        'type': 'reset',
        'value': 'Reset',
    }


class TextInputNode(InputNode):
    ATTRIBUTES = {
        'type': 'text',
    }


class CheckboxNode(InputNode):
    ATTRIBUTES = {
        'type': 'checkbox',
    }


class TextAreaNode(Node):
    TAG_NAME = 'textarea'

    def __repr__(self):
        return self.__str__(
            skip_value=True,
            node_string=self.attributes.get('value', ''),
        )


class SelectNode(Node):
    TAG_NAME = 'select'


class OptionNode(Node):
    TAG_NAME = 'option'


# complex html nodes ##########################################################
class Img(Node):
    TAG_NAME = 'img'
    SELF_CLOSING_TAG = True


class A(Node):
    TAG_NAME = 'a'

    def __init__(self, *args, interactive=None, **kwargs):
        super().__init__(*args, **kwargs)

        if interactive is not None:
            self.interactive = interactive

    @property
    def interactive(self):
        return self.ignore

    @interactive.setter
    def interactive(self, value):
        self.ignore = value

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
