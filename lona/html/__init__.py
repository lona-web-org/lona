from __future__ import annotations

from lona.html.nodes.inline_text_semantics import (
    Strong,
    Small,
    Time,
    Span,
    Samp,
    Ruby,
    Mark,
    Data,
    Code,
    Cite,
    Abbr,
    Wbr,
    Var,
    Sup,
    Sub,
    Kbd,
    Dfn,
    Bdo,
    Bdi,
    Rt,
    Rp,
    Em,
    Br,
    U,
    S,
    Q,
    I,
    B,
    A,
)
from lona.html.nodes.content_sectioning import (
    Section,
    Article,
    Address,
    HGroup,
    Header,
    Footer,
    Aside,
    Main,
    Nav,
    H6,
    H5,
    H4,
    H3,
    H2,
    H1,
)
from lona.html.nodes.forms import (
    Progress,
    OptGroup,
    Fieldset,
    FieldSet,
    Datalist,
    DataList,
    Output,
    Legend,
    Button,
    Meter,
    Label,
    Form,
)
from lona.html.nodes.text_content import (
    FigCaption,
    BlockQuote,
    Figure,
    Menu,
    Pre,
    Div,
    Ul,
    Ol,
    Li,
    Hr,
    Dt,
    Dl,
    Dd,
    P,
)
from lona.html.nodes.table_content import (
    ColGroup,
    Caption,
    THead,
    TFoot,
    TBody,
    Table,
    Col,
    Tr,
    Th,
    Td,
)
from lona.html.nodes.embedded_content import (
    Picture,
    Source,
    Portal,
    Object,
    IFrame,
    Embed,
)
from lona.html.nodes.forms.inputs import (
    NumberInput,
    TextInput,
    TextArea,
    CheckBox,
    Submit,
)
from lona.html.nodes.image_and_multimedia import (
    Video,
    Track,
    Audio,
    Area,
    Map,
    Img,
)
from lona.html.nodes.document_metadata import (
    Title,
    Style,
    Meta,
    Link,
    Head,
    Base,
)
from lona.html.nodes.interactive_elements import Summary, Details, Dialog
from lona.html.nodes.forms.radio_button import RadioButton, RadioGroup
from lona.html.nodes.scripting import NoScript, Script, Canvas
from lona.html.nodes.forms.select2 import Select2, Option2
from lona.html.nodes.web_components import Template, Slot
from lona.html.parsing import NodeHTMLParser, parse_html
from lona.html.nodes.forms.select import Select, Option
from lona.html.nodes.demarcating_edits import Ins, Del
from lona.html.nodes.svg_and_mathml import Math, SVG
from lona.events.event_types import *  # NOQA: F403
from lona.html.nodes.sectioning_root import Body
from lona.html.nodes.raw_nodes import RawHTML
from lona.html.widgets import HTML as HTML1
from lona.html.parsing import HTML as HTML2
from lona.compat import get_client_version
from lona.html.widget import Widget
from lona.html.node import Node

NODE_CLASSES: dict[str, type[Node]] = {
    # source: https://developer.mozilla.org/en-US/docs/Web/HTML/Element

    # document metadata
    'base': Base,
    'head': Head,
    'link': Link,
    'meta': Meta,
    'style': Style,
    'title': Title,

    # sectioning root
    'body': Body,

    # content sectioning
    'address': Address,
    'article': Article,
    'aside': Aside,
    'footer': Footer,
    'header': Header,
    'h1': H1,
    'h2': H2,
    'h3': H3,
    'h4': H4,
    'h5': H5,
    'h6': H6,
    'hgroup': HGroup,
    'main': Main,
    'nav': Nav,
    'section': Section,

    # text content
    'blockquote': BlockQuote,
    'dd': Dd,
    'div': Div,
    'dl': Dl,
    'dt': Dt,
    'figcaption': FigCaption,
    'figure': Figure,
    'hr': Hr,
    'li': Li,
    'menu': Menu,
    'ol': Ol,
    'p': P,
    'pre': Pre,
    'ul': Ul,

    # inline text semantics
    'a': A,
    'abbr': Abbr,
    'b': B,
    'bdi': Bdi,
    'bdo': Bdo,
    'br': Br,
    'cite': Cite,
    'code': Code,
    'data': Data,
    'dfn': Dfn,
    'em': Em,
    'i': I,
    'kbd': Kbd,
    'mark': Mark,
    'q': Q,
    'rp': Rp,
    'rt': Rt,
    'ruby': Ruby,
    's': S,
    'samp': Samp,
    'small': Small,
    'span': Span,
    'strong': Strong,
    'sub': Sub,
    'sup': Sup,
    'time': Time,
    'u': U,
    'var': Var,
    'wbr': Wbr,

    # image and multimedia
    'area': Area,
    'audio': Audio,
    'img': Img,
    'map': Map,
    'track': Track,
    'video': Video,

    # embedded content
    'embed': Embed,
    'iframe': IFrame,
    'object': Object,
    'picture': Picture,
    'portal': Portal,
    'source': Source,

    # SVG and MathMl
    'svg': SVG,
    'math': Math,

    # scripting
    'canvas': Canvas,
    'noscript': NoScript,
    'script': Script,

    # demarcating edits
    'del': Del,
    'ins': Ins,

    # table content
    'caption': Caption,
    'col': Col,
    'colgroup': ColGroup,
    'table': Table,
    'tbody': TBody,
    'td': Td,
    'tfoot': TFoot,
    'th': Th,
    'thead': THead,
    'tr': Tr,

    # forms
    'button': Button,
    'datalist': Datalist,
    'fieldset': Fieldset,
    'form': Form,
    'label': Label,
    'legend': Legend,
    'meter': Meter,
    'optgroup': OptGroup,
    'option': Option,
    'output': Output,
    'progress': Progress,
    'select': Select,
    'textarea': TextArea,

    # interactive elements
    'details': Details,
    'dialog': Dialog,
    'summary': Summary,

    # web components
    'slot': Slot,
    'template': Template,
}

INPUT_NODE_CLASSES: dict[str, type[Node]] = {
    'text': TextInput,
    'number': NumberInput,
    'submit': Submit,
    'checkbox': CheckBox,
}

# TODO: remove in 2.0
FUTURE_NODE_CLASSES: dict[str, type[Node]] = {
    'select': Select2,
    'option': Option2,
    'datalist': DataList,
    'fieldset': FieldSet,
}

SELF_CLOSING_TAGS: list[str] = [
    # source: https://developer.mozilla.org/en-US/docs/Glossary/Void_element

    'area',
    'base',
    'br',
    'col',
    'embed',
    'hr',
    'img',
    'input',
    'link',
    'meta',
    'source',
    'track',
    'wbr',
]

NodeHTMLParser._setup_node_classes_cache()


def HTML(*args, **kwargs):
    if get_client_version() == 1:
        return HTML1(*args, **kwargs)

    return HTML2(*args, **kwargs)
